library(tidyverse)
library(googlesheets4)

load_packages <- function() {
  packages <- c("tidyverse", "ggplot2", "dplyr", "readr", "lubridate", "stringr")
  lapply(packages, require, character.only = TRUE)
}


format_cpf_cnpj <- function(x) {
  x <- gsub("\\D", "", x)
  if (nchar(x) == 11) {
    return(sprintf("%s.%s.%s-%s", substr(x,1,3), substr(x,4,6), substr(x,7,9), substr(x,10,11)))
  } else if (nchar(x) == 14) {
    return(sprintf("%s.%s.%s/%s-%s", substr(x,1,2), substr(x,3,5), substr(x,6,8), substr(x,9,12), substr(x,13,14)))
  } else {
    return(x)
  }
}


load_packages()

setwd("C:/Users/vitor/inter-scraping")

sheet_id = '1jT-q_aEqR9OxcfsYna8UAAwXauH3-9QiM4lI-l6hHYU'

# Ler o arquivo Excel do Google Sheets com base no sheet_id
full_db <- read_sheet(ss = sheet_id, sheet = "Página2") %>%
  select(-where(~ is.logical(.)))

# Transformar a coluna 'valor' em double, mas verificar se está no formato
# R$ ... e transformar para número
full_db %>%
  mutate(
    #Valor = case_when(
      #str_detect(Valor, ",") ~ str_replace_all(str_replace_all(Valor, "\\.", ""), ",", "."),
    #  TRUE ~ Valor
    #),
    Valor = str_remove(Valor, "R\\$ "),
    Valor = as.numeric(Valor),
    Data = as.Date(Data)
  ) -> full_db

# Ler apenas os arquivos all_data... .csv no database
db_files = list.files('./database/', pattern = '\\.csv$', full.names = TRUE)

all_data = list()

for (db_file in db_files) {
  file_name <- basename(db_file)
  file_name_no_ext <- str_remove(file_name, "\\.csv$")
  parts <- str_split(file_name_no_ext, "_", n = 3, simplify = TRUE)
  cpf_cnpj <- parts[1]
  nome <- parts[2]
  df <- read_csv2(db_file, col_names = TRUE)
  df$cpf_cnpj <- cpf_cnpj
  df$nome <- nome
  all_data[[length(all_data) + 1]] <- df
}

db_new <- bind_rows(all_data)

db_new %>% 
  filter(Status == 'Aprovada') %>% 
  rowwise() %>% 
  mutate(cpf_cnpj = format_cpf_cnpj(cpf_cnpj)) %>% 
  ungroup %>% 
  mutate(
    date = substr(`Data e hora`, 1, 10) %>% dmy %>% format('%Y-%m-%d')  # <-- Apenas data, formato yyyy-mm-dd
  ) %>% 
  select(date, Bandeira, Valor, cpf_cnpj, nome, Tipo, `Numero Parcelas`, Id) %>% 
  rename(brand = Bandeira, value = Valor, installments = `Numero Parcelas`, payment_method = Tipo) %>% 
  distinct(Id, .keep_all = T)  -> db_mine

db_clientes <- readxl::read_excel('Dados Clintes Inter.xlsx')

db_clientes %>% 
  select(name, cpf_cnpj, state_name, fantasy_name, branch_of_activity,
  cep, phone, email, city_name, street_name, status, bank_name, agency,
  account_dv, account_type) -> db_clientes_data

db_mine %>% 
  left_join(db_clientes_data, by = 'cpf_cnpj') -> final_db

# Deixar banco de dados com esse formato: 
# CPF/CNPJ	Valor	Data	Column 10	Meio de Pagamento	Nº de Parcelas	Bandeira	Nome	UF	Nome Fantasia

final_db %>% 
  transmute(
    `CPF/CNPJ` = cpf_cnpj,
    `Valor` = value,
    `Data` = as.character(date),
    `Column 10` = NA, # Substitua por coluna real se necessário
    `Meio de Pagamento` = payment_method,
    `Nº de Parcelas` = installments,
    `Bandeira` = brand,
    `Nome` = nome,
    `UF` = state_name,
    `Nome Fantasia` = fantasy_name,
    `Ramo de Atividade` = branch_of_activity,
    `CEP` = cep,
    `Telefone` = phone,
    `Email` = email,
    `Cidade` = city_name,
    `Logradouro` = street_name,
    `Status` = status,
    `Banco` = bank_name,
    `Agência` = agency,
    `Conta DV` = account_dv,
    `Tipo de Conta` = account_type,
     Id = Id
  ) %>% 
  select(-where(~ is.logical(.))) %>% 
  mutate(Data = ymd(Data)) -> result_db

# O join agora funcionará pois ambos os lados têm Data como <character> no formato yyyy-mm-dd
full_db %>%
  full_join(result_db, by = names(.)) %>% 
  distinct(Id, .keep_all = T) %>%  
  arrange(Data) -> final_db_sheet


# Salva localmente (opcional) com tratamento de erro
tryCatch({
  writexl::write_xlsx(final_db_sheet, 'transaction_with_type_and_brand.xlsx')
}, error = function(e) {
  message("Não foi possível salvar 'transaction_with_type_and_brand.xlsx'. O arquivo pode estar aberto ou protegido. Erro: ", e$message)
  # Alternativamente, salve com outro nome:
  alt_path <- paste0('transaction_with_type_and_brand_', format(Sys.time(), "%Y%m%d%H%M%S"), '.xlsx')
  writexl::write_xlsx(result_db, alt_path)
  message("Arquivo salvo como: ", alt_path)
})

# Escreve no Google Sheets (substitui a aba "Transações")
sheet_write(final_db_sheet, ss = sheet_id, sheet = "Página2")
