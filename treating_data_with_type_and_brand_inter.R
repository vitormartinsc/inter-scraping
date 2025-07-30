library(tidyverse)
library(googlesheets4)
library(readxl)
library(lubridate)

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

setwd("~/inter-scraping")

sheet_id = '1jT-q_aEqR9OxcfsYna8UAAwXauH3-9QiM4lI-l6hHYU'

# Ler o arquivo Excel do Google Sheets com base no sheet_id
full_db <- read_sheet(ss = sheet_id, sheet = "Página2") %>%
  select(-where(~ is.logical(.)))

# Transformar a coluna 'valor' em double, mas verificar se está no formato
# R$ ... e transformar para número
full_db %>%
  mutate(
    Valor = str_remove(Valor, "R\\$ "),
    Valor = as.numeric(Valor),
    Data = as.Date(Data)
  ) -> full_db

# Ler o db_inter_merged.csv
inter_db <- read_csv('db_inter_merged.csv', col_types = cols())

# Ajustar nomes e tipos para compatibilidade
inter_db <- inter_db %>%
  mutate(
    cpf_cnpj = as.character(cpf_cnpj),
    cpf_cnpj = str_replace_all(cpf_cnpj, '\\D', ''),
    cpf_cnpj = case_when(
      nchar(cpf_cnpj) <= 11 ~ str_pad(cpf_cnpj, 11, pad = '0'),
      nchar(cpf_cnpj) > 11 ~ str_pad(cpf_cnpj, 14, pad = '0'),
      TRUE ~ cpf_cnpj
    )) %>%
    rowwise() %>%
    mutate(cpf_cnpj = format_cpf_cnpj(cpf_cnpj)) %>%
    ungroup() %>%
    mutate(
      date = as.Date(date, format = "%Y-%m-%d"),
      value = as.numeric(value),
      installments = as.numeric(installments)
    ) 

# Montar db_mine igual ao treating_data_with_type_and_brand.R
inter_db %>%
  select(date, brand, value, cpf_cnpj, nome, payment_method, installments, Id) %>%
  rename(
    brand = brand,
    value = value,
    installments = installments,
    payment_method = payment_method,
    nome = nome,
    cpf_cnpj = cpf_cnpj,
    date = date,
    Id = Id
  ) %>%
  distinct(Id, .keep_all = T) -> db_mine

# Carregar clientes
clientes <- readxl::read_excel('Dados Clintes Inter.xlsx')
clientes %>%
  select(name, cpf_cnpj, state_name, fantasy_name, branch_of_activity,
         cep, phone, email, city_name, street_name, status, bank_name, agency,
         account_dv, account_type) -> db_clientes_data

db_mine %>%
  left_join(db_clientes_data, by = 'cpf_cnpj') -> final_db

# Formatar banco final
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
  mutate(Nome = as.character(Nome)) %>%
  select(-where(~ is.logical(.))) %>%
  mutate(Data = ymd(Data)) -> result_db

# O join agora funcionará pois ambos os lados têm Data como <character> no formato yyyy-mm-dd
final_db_sheet <- full_db %>%
  full_join(result_db, by = names(.)) %>%
  distinct(Id, .keep_all = T) %>%  
  arrange(Data)

# Preencher Nome se for NA, buscando pelo CPF/CNPJ no banco de clientes
final_db_sheet <- final_db_sheet %>%
  mutate(Nome = if_else(is.na(Nome) | Nome == "", 
                        db_clientes_data$name[match(`CPF/CNPJ`, db_clientes_data$cpf_cnpj)],
                        Nome),
        `Meio de Pagamento` = ifelse(`Meio de Pagamento` == 'Não se aplica', 'Pix', `Meio de Pagamento`))

# Salva localmente (opcional) com tratamento de erro
tryCatch({
  writexl::write_xlsx(final_db_sheet, 'transaction_with_type_and_brand_from_inter_db.xlsx')
}, error = function(e) {
  message("Não foi possível salvar 'transaction_with_type_and_brand_from_inter_db.xlsx'. O arquivo pode estar aberto ou protegido. Erro: ", e$message)
  alt_path <- paste0('transaction_with_type_and_brand_from_inter_db_', format(Sys.time(), "%Y%m%d%H%M%S"), '.xlsx')
  writexl::write_xlsx(result_db, alt_path)
  message("Arquivo salvo como: ", alt_path)
})

# Escreve no Google Sheets (substitui a aba "Transações")
sheet_write(final_db_sheet, ss = sheet_id, sheet = "Página2")
