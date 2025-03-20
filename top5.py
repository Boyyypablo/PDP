import pandas as pd
import matplotlib.pyplot as plt  # Adicionando a importação do matplotlib

# Caminho do arquivo CSV ou Excel
file_path = r"C:\Users\pablo.basilio\Downloads\PDP cursos refinados (version 1).csv"  # Ajuste conforme necessário

# Usar o read_csv se o arquivo for CSV
try:
    df = pd.read_csv(file_path, delimiter=';', on_bad_lines='skip', quotechar='"')  # Ignorar linhas problemáticas

    # Exibir as primeiras linhas para verificar se a planilha foi carregada corretamente
    print(df.head())

except Exception as e:
    print(f"Ocorreu um erro ao ler o arquivo CSV: {e}")

# Combinar todas as colunas de temáticas em uma série
tematicas = df[['Tematicas dos cursos', 'Tematicas dos cursos2', 'Tematicas dos cursos3',
                'Tematicas dos cursos4', 'Tematicas dos cursos5', 'Tematicas dos cursos6']].stack()

# Contar as ocorrências de cada temática
contagem_tematicas = tematicas.value_counts()

# Exibir o resultado do agrupamento de temáticas
print("Temáticas e suas contagens agregadas:")
print(contagem_tematicas)

# Gerar um gráfico de barras para as temáticas agrupadas
contagem_tematicas.plot(kind='bar', color='skyblue', edgecolor='black')
plt.title('Contagem de Temáticas Agregadas')
plt.xlabel('Temáticas')
plt.ylabel('Número de Ocorrências')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# (Opcional) Salvar as temáticas agregadas em um novo arquivo Excel
contagem_tematicas.to_excel("tematicas_agregadas.xlsx", index=True)
