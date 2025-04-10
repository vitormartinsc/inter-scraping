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

setwd('C:/Users/servi/inter-scraping//')

list(
  read_csv('data.csv'),
  read_csv('data_02.csv'),
  read_csv('data_03.csv'),
  read_csv('data_04.csv')
) %>% 
  plyr::join_all(type = 'full') %>%
  filter(value > 0) %>% 
  rename(date_raw = date) %>% 
  distinct(name, value, date_raw, .keep_all = T) -> df

df_separado <- df %>%
  mutate(
    date = str_extract(date_raw, "\\d{4}, \\d{1,2}, \\d{1,2}") %>%
      str_replace_all(", ", "-") %>%
      as.Date(format = "%Y-%m-%d"),
    type = str_extract(date_raw, "'(.*?)'") %>%
      str_replace_all("'", ""),
    number_of_installments = date_raw %>% substr(., nchar(.) - 2, nchar(.) - 1) %>% 
      as.numeric()
  ) %>% 
  select(-date_raw) %>% 
  filter(!is.na(number_of_installments)) 

df_separado %>% 
  purrr::set_names('CPF/CNPJ', 'Nome', "Valor Transação", 'Data', 'Meio de Pagamento', 'Nº de Parcelas') %>% 
  writexl::write_xlsx('raw_data.xlsx')

df_separado %>% 
  group_by(type, date, number_of_installments) %>% 
  summarise(value = sum(value)) %>% 
  ungroup() %>% 
  arrange(date) %>% 
  purrr::set_names('Meio de Pagamento', 'Data', 'Nº de Parcelas', 'Valor Total') %>% 
  writexl::write_xlsx('grouped_data.xlsx')


