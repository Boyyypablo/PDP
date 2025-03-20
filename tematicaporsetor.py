import pandas as pd

# Corrija este caminho com o nome exato do arquivo salvo
file_path = r"C:\Users\pablo.basilio\Downloads\setorgeral.xlsm"
# Adicione um tratamento de erro claro
try:
    df = pd.read_excel(file_path)
except FileNotFoundError:
    print(f"O arquivo não foi encontrado no caminho especificado: {file_path}")
    exit()

# Exibir as primeiras linhas para verificar
print(df.head())

# Combina as colunas em formato longo
df_melted = df.melt(id_vars=["Setor"], value_vars=["Tematicas dos cursos", "Tematicas dos cursos2",
                                                   "Tematicas dos cursos3", "Tematicas dos cursos4",
                                                   "Tematicas dos cursos5", "Tematicas dos cursos6"],
                    var_name="Ordem", value_name="Tematica").dropna()

# Agrupa e conta as ocorrências das temáticas por setor
df_grouped = df_melted.groupby(["Setor", "Tematica"]).size().reset_index(name="Quantidade")

# Para obter a temática mais pedida por setor
idx = df_grouped.groupby("Setor")["Quantidade"].idxmax()
top_tematicas_setor = df_grouped.loc[idx]

# Salva o resultado
top_tematicas_setor.to_excel("111111tematicas_mais_pedidas_por_setor.xlsx", index=False)

# Exibe resultado
print(top_tematicas_setor)
