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

# Carrega configurações
source("config.R")
load_env()

setwd("C:/Users/Vitor/inter-scraping/")

# Usa função segura para obter ID da planilha
sheet_id <- get_sheet_id("equipment")

# 📥 Baixa o arquivo Excel do Google Drive
temp_file <- tempfile(fileext = ".xlsx")
drive_download(as_id(sheet_id), path = temp_file, overwrite = TRUE)

#### ATUALIZANDO O INTER

sheet_name <- "Base inter"  # Nome da sheet que será alterada

# 📖 Carrega o arquivo Excel inteiro (com todas as sheets)
wb <- loadWorkbook(temp_file)

db_inter <- read_excel(temp_file, sheet = sheet_name, skip = 3) # Ajuste a aba conforme necessário

new_db_inter = read_csv('data.csv')

new_db_inter %>% 
  filter(value > 0) %>% 
  rename(Nome = name) %>% 
  distinct(`cpf/cnpj`, date, .keep_all = T) %>% 
  group_by(`cpf/cnpj`) %>% 
  mutate(
    had_transacitons = sum(value) > 0,
    date = format(date, '%d/%m/%Y')
  ) %>% 
  ungroup %>% 
  filter(had_transacitons) %>% 
  select(-had_transacitons, -Nome) %>% 
  spread(date, value) %>% 
  rename('CPF ou CNPJ' = 1) -> new_db_transformed

date_cols <- colnames(new_db_transformed)[2:ncol(new_db_transformed)]  # Excluindo a primeira coluna (CNPJ)
date_cols <- intersect(date_cols, colnames(db_inter))

new_db_transformed %>% 
  select(1, 2) %>% 
  spread(1, 2) %>% 
  as.list() -> cpf_cnpj_list

# Atualizar os valores das colunas de data em db
db_inter %>% 
  select(-all_of(date_cols)) %>% 
  full_join(new_db_transformed, by = 'CPF ou CNPJ') %>% 
  rowwise() %>% 
  mutate(CLIENTE = ifelse(is.na(CLIENTE), cpf_cnpj_list[`CPF ou CNPJ`] %>% unlist %>% toupper(), CLIENTE)) %>% 
  ungroup %>% 
  arrange(CLIENTE) %>% 
  gather(date, value, -c(names(.)[1: 5])) %>% 
  mutate(date = dmy(date)) %>% 
  arrange(date) %>% 
  mutate(date = format(date, '%d/%m/%Y')) %>%
  mutate(
    date = factor(date, levels = .$date %>% unique),
    value = as.numeric(value), 
    `DIAS TRANSACIONADOS` = as.numeric(`DIAS TRANSACIONADOS`),
    TOTAL = as.numeric(TOTAL)
  ) %>%  
  filter(!is.na(date)) %>% 
  spread(date, value) %>% 
  mutate(`Nº` = row_number()) -> db_inter_final


# 📌 Escreve os dados dentro do intervalo sem apagar o restante
writeData(wb, sheet = sheet_name, x = db_inter_final, startRow = 4, startCol = 1, colNames = TRUE)

# 💾 Salva as alterações
saveWorkbook(wb, temp_file, overwrite = TRUE)

# 📤 Reenvia para o Google Drive
drive_update(as_id(sheet_id), media = temp_file)

#### ATUALIZANDO A OWN

sheet_name <- "Base own"  # Nome da sheet que será alterada

db_own <- read_excel(temp_file, sheet = sheet_name, skip = 2) # Ajuste a aba conforme necessário

new_db_own <- read_csv('relatorio_diario_own.csv')

new_db_own %>% 
  select(`CNPJ Estabelecimento`, `Razão Social`,`Data Métrica`, `VGT`) %>% 
  rename(date = 3, value = 4) %>% 
  mutate(
    date = dmy(date),
    value = value %>% 
      str_replace(' ', '') %>% 
      str_replace('R\\$', '') %>% 
      str_replace('\\.', '') %>% 
      str_replace(',', '.') %>% 
      as.numeric(),
    `CNPJ Estabelecimento` = as.numeric(`CNPJ Estabelecimento`)
  ) %>% 
  group_by(`CNPJ Estabelecimento`, `Razão Social`, date) %>% 
  summarise(value = sum(value), .groups = 'drop') %>% 
  rename('RAZÃO SOCIAL' = `Razão Social`) -> new_db_own_transformed

db_own %>% 
  gather(date, value, -c(1:6)) %>% 
  group_by(`Nome Fantasia`) %>% 
  mutate(`RAZÃO SOCIAL` = ifelse(is.na(`RAZÃO SOCIAL`), first(`RAZÃO SOCIAL`), `RAZÃO SOCIAL`)) %>% 
  mutate(date = if_else(
    grepl('/', date), 
    dmy(date), 
    as.Date(as.numeric(date), origin = "1899-12-30")
  ))  %>% 
  filter(!date %in% unique(new_db_own_transformed$date)) %>% 
  full_join(new_db_own_transformed) %>% 
  mutate(value = ifelse(is.na(value), 0, value)) %>% 
  group_by(`CNPJ Estabelecimento`) %>% 
  mutate(
    `Nº` = ifelse(is.na(`Nº`), first(`Nº`), `Nº`),
    #`...3` = ifelse(is.na(`...3`), first(`...3`), `...3`),
    `Nome Fantasia` = ifelse(is.na(`Nome Fantasia`), first(`Nome Fantasia`), `Nome Fantasia`),
    ACM = sum(value),
  ) %>% 
  group_by(date, `CNPJ Estabelecimento`) %>% 
  mutate(n = ifelse(value > 0, 1, 0)) %>%
  group_by(`CNPJ Estabelecimento`) %>% 
  mutate(`Dias Transacionados` = sum(n)) %>% 
  ungroup %>% 
  select(-n) %>% 
  arrange(date) %>% 
  mutate(date = format(date, '%d/%m/%Y')) %>% 
  mutate(date = factor(date, levels = .$date %>% unique)) %>% 
  group_by(date, `CNPJ Estabelecimento`) %>% 
  filter(value == max(value)) %>% 
  ungroup %>% 
  distinct(date, value, `CNPJ Estabelecimento`, .keep_all = T) %>% 
  spread(date, value) %>% 
  mutate_if(is.numeric, ~ifelse(is.na(.), 0, .)) -> db_own_final

# 📌 Escreve os dados dentro do intervalo sem apagar o restante
writeData(wb, sheet = sheet_name, x = db_own_final, startRow = 3, startCol = 1, colNames = TRUE)

# 💾 Salva as alterações
saveWorkbook(wb, temp_file, overwrite = TRUE)

# 📤 Reenvia para o Google Drive
drive_update(as_id(sheet_id), media = temp_file)
