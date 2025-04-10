load_packages()
setwd('C:/Users/servi/Downloads/')
files_path = 'C:/Users/servi/Downloads/'
files <- list.files(path = files_path, pattern = "^PAGO_Transações_.*", full.names = TRUE)

all_dfs = list()


for (file in files) {
  
  df = read_csv2(file)
  all_dfs[[file]] = df
  
}

db_all = plyr::join_all(all_dfs, type = 'full')

db_all %>% 
  select(`Data e hora`, Valor, Tipo, `Numero Parcelas`, Status) %>% 
  distinct(`Data e hora`, Tipo, Valor, .keep_all = T) %>% 
  set_names(c('date', 'value', 'type', 'number', 'status')) %>% 
  mutate(date = substr(date, 1, 10) %>% dmy) %>% 
  filter(date <= '2025-03-03', status == 'Aprovada') -> db

library(ggplot2)
library(dplyr)


# Transformação dos dados
db %>%
  group_by(date) %>% 
  summarise(value = sum(value)) %>% 
  mutate(date = weekdays(date)) %>% 
  mutate(date = factor(date, levels = .$date, ordered = TRUE)) %>%  # Fator ordenado
  ggplot(aes(x = date, y = value)) + 
  geom_col(fill = "#1B2A41") +  # Azul escuro
  geom_label(aes(label = value), vjust = -0.2, color = "white", fill = "#1B2A41", label.size = 0.3) +  # Valores no topo
  labs(
    title = "Valor Total de Transações por Dia da Semana",
    x = "Dia da Semana",
    y = "Valor Total"
  ) +
  theme_minimal(base_size = 14) +  
  theme(
    plot.title = element_text(hjust = 0.5, face = "bold", color = "black", size = 16),
    axis.text = element_text(color = "black"),
    axis.title = element_text(color = "black"),
    plot.background = element_rect(fill = "white", color = NA),  # Fundo branco
    panel.background = element_rect(fill = "white", color = NA),
    panel.grid.major = element_line(color = "grey90"),
    panel.grid.minor = element_blank()
  ) # Tons de 

# Transformação dos dados
db %>%
  group_by(date) %>% 
  summarise(value = n()) %>% 
  mutate(date = weekdays(date)) %>% 
  mutate(date = factor(date, levels = .$date, ordered = TRUE)) %>%  # Fator ordenado
  ggplot(aes(x = date, y = value)) + 
  geom_col(fill = "#1B2A41") +  # Azul escuro
  geom_label(aes(label = value), vjust = -0.2, color = "white", fill = "#1B2A41", label.size = 0.3) +  # Valores no topo
  labs(
    title = "Quantidade de Transações Carnaval",
    x = "Dia da Semana",
    y = "Quantidade Total"
  ) +
  theme_minimal(base_size = 14) +  
  theme(
    plot.title = element_text(hjust = 0.5, face = "bold", color = "black", size = 16),
    axis.text = element_text(color = "black"),
    axis.title = element_text(color = "black"),
    plot.background = element_rect(fill = "white", color = NA),  # Fundo branco
    panel.background = element_rect(fill = "white", color = NA),
    panel.grid.major = element_line(color = "grey90"),
    panel.grid.minor = element_blank()
  ) # Tons de azul


# Definindo uma paleta de cores vibrantes
cores_vibrantes <- c("#E63946", "#457B9D", "#F4A261", "#2A9D8F", "#E76F51", "#A8DADC", "#1D3557")

# Agrupando os dados
df_pizza <- db %>% 
  group_by(type) %>% 
  summarise(n = n()) %>% 
  mutate(label = paste0(type, " (", n, ")"))  # Criando rótulos com nome + quantidade

# Criando o gráfico de pizza
ggplot(df_pizza, aes(x = "", y = n, fill = type)) +
  geom_col(width = 1, color = "white") +  # Criando fatias com separação branca
  coord_polar(theta = "y") +  # Transforma em pizza
  geom_text(aes(label = label), position = position_stack(vjust = 0.5), color = "white", size = 5, fontface = "bold") +  # Rótulos no centro das fatias
  labs(title = "Quantidade de Transações por Meio de Pagamento") +
  theme_void() +  # Remove eixos e grids para um visual limpo
  theme(
    plot.title = element_text(hjust = 0.5, face = "bold", size = 16, color = "black"),
    legend.position = "none"  # Oculta a legenda (opcional)
  ) +
  scale_fill_manual(values = rep(cores_vibrantes, length.out = length(unique(df_pizza$type))))  # Aplica cores vibrantes


# Agrupando os dados
df_pizza <- db %>% 
  group_by(type) %>% 
  summarise(n = sum(value)) %>% 
  mutate(label = paste0(type, " (R$ ", n, ")"))  # Criando rótulos com nome + quantidade

# Criando o gráfico de pizza
ggplot(df_pizza, aes(x = "", y = n, fill = type)) +
  geom_col(width = 1, color = "white") +  # Criando fatias com separação branca
  coord_polar(theta = "y") +  # Transforma em pizza
  geom_text(aes(label = label), position = position_stack(vjust = 0.5), color = "white", size = 5, fontface = "bold") +  # Rótulos no centro das fatias
  labs(title = "Valor Total por Meio de Pagamento") +
  theme_void() +  # Remove eixos e grids para um visual limpo
  theme(
    plot.title = element_text(hjust = 0.5, face = "bold", size = 16, color = "black"),
    legend.position = "none"  # Oculta a legenda (opcional)
  ) +
  scale_fill_manual(values = rep(cores_vibrantes, length.out = length(unique(df_pizza$type))))  # Aplica cores vibrantes

db %>% filter(status == 'Aprovada') %>% 
  group_by(type, date) %>% 
  summarise(value = sum(value), .groups = 'drop') %>% 
  arrange(date) %>% 
  mutate(date = format(date, '%d/%m/%Y')) %>% 
  mutate(date = factor(date, levels = .$date %>% unique)) %>% 
  spread(date, value) %>% 
  writexl::write_xlsx('Tpv Carnaval Detalhado.xlsx')

