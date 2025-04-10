# Solicitando o limite total ao usuário
total_limit = float(input("Digite o seu limite disponível no cartão de crédito: ").replace(",", "."))

# Tabela de taxas de juros (em porcentagem)
interest_rates = {
    1: 23.00, 
    3: 55.10, 
    10: 55.80, 
    18: 67.94
}

# Função para calcular o valor máximo que pode ser sacado
def calculate_max_withdraw(limit, rate):
    return limit / (1 + rate / 100)

# Dicionários para armazenar os valores calculados
max_withdrawals = {}
installment_values = {}

# Calculando os valores para cada parcelamento
for installment in [1, 3, 10, 18]:
    max_withdraw = calculate_max_withdraw(total_limit, interest_rates[installment])
    installment_value = max_withdraw / installment

    # Formatando para reais (R$)
    max_withdrawals[installment] = f"R$ {max_withdraw:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    installment_values[installment] = f"R$ {installment_value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Exibindo a mensagem formatada
print(f"""
Obrigado pela resposta! Com esse limite disponível, você pode sacar até {max_withdrawals[1]} para pagar em uma parcela. 
Mas se preferir outras alternativas de parcelamento, confira nossas opções: 🎯💰

📌 Parcele do seu jeito, de 1x até 18x! Veja alguns exemplos:

✅ Saque de {max_withdrawals[3]} para pagar em 3 parcelas de {installment_values[3]}!

✅ Saque de {max_withdrawals[10]} para pagar em 10 parcelas de {installment_values[10]}!

✅ Saque de {max_withdrawals[18]} para pagar em 18 parcelas de {installment_values[18]}!
""")
