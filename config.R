# config.R - Configurações para scripts R
# Use variáveis de ambiente para proteger IDs sensíveis

get_sheet_id <- function(sheet_name) {
  # Tenta ler da variável de ambiente primeiro
  env_var <- paste0(toupper(sheet_name), "_SHEET_ID")
  sheet_id <- Sys.getenv(env_var)
  
  if (sheet_id == "") {
    stop(paste("❌ ERRO: ID da planilha não configurado!", 
               "Configure a variável", env_var, "no arquivo .env"))
  }
  
  return(sheet_id)
}

# Função para carregar variáveis de ambiente do arquivo .env
load_env <- function() {
  if (file.exists(".env")) {
    readRenviron(".env")
  } else {
    warning("⚠️ Arquivo .env não encontrado. Use .env.example como referência.")
  }
}
