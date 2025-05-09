library(tidyverse)

load_packages <- function() {
  packages <- c("tidyverse", "ggplot2", "dplyr", "readr", "lubridate", "stringr")
  lapply(packages, require, character.only = TRUE)
}

load_packages()

setwd("C:/Users/vitor/inter-scraping")
# Ler apenas os arquivos all_data... .csv no database
db_files = list.files('./database/') %>% 
  str_subset('all_data') %>% 
  str_subset('.csv') 

all_data = c()

for (db_file in db_files) {
  
  all_data[[length(all_data) + 1]] <- read_csv(paste0('./database/', db_file), col_names = TRUE)
  
}

db = plyr::join_all(all_data, type = 'full')

db %>% 
  na.omit %>% 
  group_by(date) %>% 
  summarise(value = sum(value)) %>% tail

db_clientes <- readxl::read_excel('Dados Clintes Inter.xlsx')

db_clientes %>% 
  select(name, cpf_cnpj, state_name, fantasy_name) -> db_clientes_data

db %>% 
  na.omit %>% 
  rename(cpf_cnpj = 1) %>% 
  select(-name) %>% 
  left_join(db_clientes_data, by = 'cpf_cnpj') %>%
  writexl::write_xlsx('transaction_with_type_and_brand.xlsx')
