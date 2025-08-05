#!/usr/bin/env python3
import pandas as pd

# Teste da lógica de keep='last'
print("Testando lógica de keep='last'...")

# Simula dados antigos do Google Sheets
old_data = pd.DataFrame({
    'CPF/CNPJ': ['259.644.388-06'],
    'Nome': ['Lana Rose Ramos da Silva'],
    'UF': [''],  # Vazio
    'Telefone': [''],  # Vazio
    'Id': [123]
})

# Simula dados novos do Inter
new_data = pd.DataFrame({
    'CPF/CNPJ': ['259.644.388-06'],
    'Nome': ['Lana Rose Ramos da Silva'],
    'UF': ['MG'],  # Preenchido
    'Telefone': ['(31) 98218-3600'],  # Preenchido
    'Id': [123]
})

print("Dados antigos (Google Sheets):")
print(old_data)
print("\nDados novos (Inter):")
print(new_data)

# Concatena e remove duplicatas mantendo o último (keep='last')
combined = pd.concat([old_data, new_data], ignore_index=True)
result = combined.drop_duplicates(subset=['Id'], keep='last')

print("\nResultado final (deve manter dados novos):")
print(result)
