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

df2 = read_csv('new_equipment_data.csv')

# Usa função segura para obter ID da planilha
sheet_id <- get_sheet_id("equipment")

# 📥 Baixa o arquivo Excel do Google Drive
temp_file <- tempfile(fileext = ".xlsx")
drive_download(as_id(sheet_id), path = temp_file, overwrite = TRUE)
wb <- loadWorkbook(temp_file)

sheet_name = 'Base inter'

db_inter <- read_excel(temp_file, sheet = sheet_name, skip = 3) 

normalize_name <- function(name) {
  name %>%
    stringi::stri_trans_general("Latin-ASCII") %>%  # remove acentos
    tolower() %>%                                   # para minúsculas
    stringr::str_replace_all("[^a-z\\s]", "") %>%   # remove tudo que não for letra ou espaço
    stringr::str_squish()                        # remove espaços duplicados
}

df2 <- df2 %>% mutate(name_normalized = normalize_name(name))
db_inter <- db_inter %>% mutate(name_normalized = normalize_name(CLIENTE),
                                name_normalized = str_replace(name_normalized, 'fernada', 'fernanda'))

# Criar uma função para calcular score
calculate_score <- function(name, crm_names) {
  name_parts <- str_split(name, " ", simplify = TRUE)
  first_name <- name_parts[1]
  surnames <- name_parts[-1]
  
  scores <- map_dbl(crm_names, function(crm_name) {
    crm_parts <- str_split(crm_name, " ", simplify = TRUE)
    if (length(crm_parts) == 0 || crm_parts[1] != first_name) return(0)
    
    sum(surnames %in% crm_parts[-1])
  })
  
  names(scores) <- crm_names
  best_match <- names(which.max(scores))
  
  if (all(scores == 0)) return(paste0('N/A:', name))
  return(best_match)
}



# Aplicar a função a todos os nomes de df2
matches <- map_chr(db_inter$name_normalized, calculate_score, crm_names = df2$name_normalized)

# Resultado com os nomes mapeados
db_inter$name_normalized <- matches

db_inter %>% 
  select(name_normalized, TOTAL) %>% 
  rename(faturamento = TOTAL) %>% 
  mutate(ticket_medio = faturamento/1.1) -> db_inter_concat

df2 %>% 
  left_join(db_inter_concat, by = 'name_normalized') %>% 
  writexl::write_xlsx('equipment_data_with_tpv.xlsx')



