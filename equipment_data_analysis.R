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

setwd("C:/Users/servi/inter-scraping")
load_packages()
df = read_csv('equipment_data.csv')

df %>% 
  na.omit %>% 
  select(-1) %>% 
  distinct(name, equipment_id, .keep_all = T) %>% 
  group_by(name) %>% 
  summarise(n = n()) %>% 
  arrange(-n)


