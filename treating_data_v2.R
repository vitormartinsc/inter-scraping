load_packages <- function() {
  message("Carregando pacotes default para projeto")
  .packages = c(
    'rbcb',
    'extrafont',
    'dplyr',
    'tidyverse',
    'Rblpapi',
    'ipeadatar',
    'readxl',
    'ggrepel',
    'quantmod',
    'alphavantager',
    'stringi',
    'vroom',
    'bizdays',
    'tidyverse',
    'lubridate'
  )
  
  for (package in .packages) {
    
    suppressMessages(require(package, character.only = TRUE))
    
  }
  
  message("Lista de pacotes carregados...")
  print(c(.packages))
  
  try(detach("package:plm", unload = TRUE), silent = T)
  
}

load_packages()
library(googlesheets4)
library(googledrive)
library(openxlsx)

setwd("C:/Users/servi/inter-scraping/")



sheet_name <- "Base (inter)"  # Nome da sheet que será alterada

# 📥 Baixa o arquivo Excel do Google Drive
temp_file <- tempfile(fileext = ".xlsx")
drive_download(as_id(sheet_id), path = temp_file, overwrite = TRUE)

# 📖 Carrega o arquivo Excel inteiro (com todas as sheets)
wb <- loadWorkbook(temp_file)

db <- read_excel(temp_file, sheet = 'Base (inter)', skip = 3) # Ajuste a aba conforme necessário


new_db = read_csv('data.csv')

new_db %>% 
  filter(value > 0) %>% 
  rename(Nome = name) %>% 
  distinct(`cpf/cnpj`, date, .keep_all = T) %>% 
  group_by(`cpf/cnpj`) %>% 
  mutate(had_transacitons = sum(value) > 0,
         date = format(date, '%d/%m/%Y')) %>% 
  ungroup %>% 
  filter(had_transacitons) %>% 
  select(-had_transacitons) %>% 
  spread(date, value) %>% 
  select(-2) %>% 
  rename('CPF ou CNPJ' = 1) -> db_transformed

date_cols <- colnames(db_transformed)[2:ncol(db_transformed)]  # Excluindo a primeira coluna (CNPJ)

# Atualizar os valores das colunas de data em db
db %>%
  select(-all_of(date_cols)) %>% 
  left_join(db_transformed, by = 'CPF ou CNPJ') %>% 
  gather(date, value, -c(names(.)[1: 5])) %>% 
  mutate(date = dmy(date)) %>% 
  arrange(date) %>% 
  mutate(date = format(date, '%d/%m/%Y')) %>%
  mutate(date = factor(date, levels = .$date %>% unique),
         value = as.numeric(value), 
         `DIAS TRANSACIONADOS` = as.numeric(`DIAS TRANSACIONADOS`),
         TOTAL = as.numeric(TOTAL)
         )%>%  
  spread(date, value) -> db_final



# 📌 Escreve os dados dentro do intervalo sem apagar o restante
writeData(wb, sheet = sheet_name, x = db_final, startRow = 4, startCol = 1, colNames = TRUE)

# 💾 Salva as alterações
saveWorkbook(wb, temp_file, overwrite = TRUE)

# 📤 Reenvia para o Google Drive
drive_update(as_id(sheet_id), media = temp_file)
