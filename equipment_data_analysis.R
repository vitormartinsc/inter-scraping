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
df_inter = read_csv('equipment_data.csv')

df_inter %>% 
  na.omit %>% 
  select(-1) %>% 
  distinct(name, equipment_id, .keep_all = T) -> df_inter

df_stock = read_excel('estoque_inter.xlsx')

df_stock %>% 
  filter(! grepl('Erro', Observação)) %>% 
  select(1, 3, 4, Status) %>% 
  select(-Status) %>% 
  na.omit %>% 
  purrr::set_names('equipment_id', 'name', 'cpf_cnpj') %>% 
  na.omit -> df_stock

equipment_ids_raw = df_raw$equipment_id


df_stock %>% 
  mutate(cpf_cnpj = gsub("\\D", "", cpf_cnpj)) %>% 
  select(equipment_id, cpf_cnpj) %>% 
  rename(stock_id = 1) -> df_stock_id

df_inter %>% 
  mutate(cpf_cnpj = gsub("\\D", "", cpf_cnpj)) %>% 
  select(equipment_id, cpf_cnpj) %>% 
  rename(inter_id = 1) -> df_inter_id

diff_stock_inter <- df_stock_id %>% 
  anti_join(df_inter_id, by = c("cpf_cnpj", "stock_id" = "inter_id"))

print(diff_stock_inter)


diff_inter_stock <- df_inter_id %>% 
  anti_join(df_stock_id, by = c("cpf_cnpj", "inter_id" = "stock_id"))

print(diff_inter_stock)
