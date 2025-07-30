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

# Carrega configurações
source("config.R")
load_env()

setwd("C:/Users/Vitor/inter-scraping/")

# Usa função segura para obter ID da planilha
sheet_id <- get_sheet_id("tpv")
db <- read_sheet(sheet_id, sheet = "Database TPV")

new_db = read_csv('data.csv')

new_db %>% 
  filter(value > 0) %>% 
  rename(Nome = name) %>% 
  distinct(`cpf/cnpj`, date, .keep_all = T) %>% 
  group_by(`cpf/cnpj`) %>% 
  mutate(had_transacitons = sum(value) > 0) %>% 
  ungroup %>% 
  filter(had_transacitons) %>% 
  select(-had_transacitons) %>% 
  spread(date, value) -> db_transformed

db_transformed %>% 
  full_join(db) %>% 
  select(`cpf/cnpj`, Nome, all_of(sort(names(.)[-c(1,2)]))) %>%  # Corrigindo select()
  mutate(across(where(is.numeric), ~ ifelse(is.na(.), 0, .))) %>% 
  gather(date, value, -Nome, -`cpf/cnpj`) %>% 
  filter(date <= today()) %>% 
  distinct(value, date, `cpf/cnpj`, .keep_all = T) %>% 
  group_by(date, `cpf/cnpj`) %>% 
  filter(value == max(value)) %>% 
  ungroup %>% 
  spread(date, value) %>%
  arrange(Nome) -> db_final
  

sheet_write(db_final, ss = sheet_id, sheet = "Database TPV")


  
