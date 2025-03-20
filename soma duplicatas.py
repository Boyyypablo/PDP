import pandas as pd

# Caminho correto do arquivo Excel
file_path = r"C:\Users\pablo.basilio\Documents\PDP projeto\PDP\tematicas_agregadas.xlsx"  # Substitua pelo caminho correto do seu arquivo
df = pd.read_excel(file_path)

# Verificar os nomes das colunas e as primeiras linhas para garantir que estamos utilizando o nome correto da coluna
print("Colunas do DataFrame:", df.columns)
print("Primeiras linhas do DataFrame:")
print(df.head())

# Agrupar as temáticas e somar as quantidades
df_sum = df.groupby('Rótulos de Linha')['Soma de count'].sum().reset_index()

# Exibir o resultado
print("Resultado da soma das temáticas:")
print(df_sum)

# Salvar o resultado somado em um novo arquivo Excel
df_sum.to_excel('tematicas_somadas.xlsx', index=False)

# Gerar um gráfico de barras para visualizar as temáticas somadas
import matplotlib.pyplot as plt

df_sum.plot(kind='bar', x='Rótulos de Linha', y='Soma de count', color='skyblue', edgecolor='black', figsize=(10, 6))
plt.title('Soma das Quantidades por Temática')
plt.xlabel('Temática')
plt.ylabel('Quantidade')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()
