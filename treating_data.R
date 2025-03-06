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

setwd("C:/Users/servi/inter-scraping/")

db = read_csv('data.csv')

db %>% 
  rename(Nome = name) %>% 
  distinct(`cpf/cnpj`, date, .keep_all = T) %>% 
  group_by(`cpf/cnpj`) %>% 
  mutate(had_transacitons = sum(value) > 0) %>% 
  ungroup %>% 
  filter(had_transacitons) %>% 
  select(-had_transacitons) %>% 
  spread(date, value) -> db_transformed

sheet_id = "1xifF_tAlbRp7kHBQyDqehH2kfyv-KxRXZBHVmGcA5qU"
sheet_write(db_transformed, ss = sheet_id, sheet = "Database TPV")


  
