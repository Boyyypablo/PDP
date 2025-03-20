from sentence_transformers import SentenceTransformer, util
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import seaborn as sns
import os


os.environ["OMP_NUM_THREADS"] = "1"


DB_USER = "postgres"
DB_PASSWORD = "12345"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "pdp"


engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")


model = SentenceTransformer('all-MiniLM-L6-v2')


cursos_transversais_referencia = [
    "Gestão Pública", "Liderança no Serviço Público", "Orçamento e Finanças Públicas",
    "Ética e Integridade", "Transformação Digital", "Redação Oficial", "Compras Governamentais",
    "Gestão de Projetos", "Transparência e Acesso à Informação", "Políticas Públicas",
    "Planejamento Estratégico"
]


embeddings_transversais = model.encode(cursos_transversais_referencia, convert_to_tensor=True)


query = "SELECT id, tematica_2 FROM minha_tabela"
df = pd.read_sql(query, engine)

df["classificacao"] = "A Revisar"


embeddings_cursos = []
cursos_nao_transversais = []
ids_nao_transversais = []


for index, row in df.iterrows():
    curso_id = row["id"]
    curso_nome = row["tematica_2"]  
    embedding_curso = model.encode(curso_nome, convert_to_tensor=True)

    
    similaridades = util.pytorch_cos_sim(embedding_curso, embeddings_transversais)

    
    max_similaridade = similaridades.max().item()

    
    if max_similaridade > 0.6:  
        df.at[index, "classificacao"] = "Transversal"
    else:
        df.at[index, "classificacao"] = "Não Transversal"
        embeddings_cursos.append(model.encode(curso_nome))  
        cursos_nao_transversais.append(curso_nome)  
        ids_nao_transversais.append(curso_id)  


with engine.connect() as conn:
    for _, row in df.iterrows():
        query_update = text("""
            UPDATE minha_tabela
            SET classificacao = :classificacao
            WHERE id = :id
        """)
        conn.execute(query_update, {"classificacao": row["classificacao"], "id": int(row["id"])})
    conn.commit()

print("Coluna 'classificacao' atualizada no banco de dados com sucesso!")


if embeddings_cursos:
    embeddings_matrix = np.array(embeddings_cursos)


    pca = PCA(n_components=2)
    embeddings_reduzidos = pca.fit_transform(embeddings_matrix)

    
    num_clusters = 5  # Número de clusters
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    df_clusters = pd.DataFrame(embeddings_reduzidos, columns=["Componente 1", "Componente 2"])
    df_clusters["Cluster"] = kmeans.fit_predict(embeddings_reduzidos)
    df_clusters["Curso"] = cursos_nao_transversais  

    
    df_clusters.to_csv("clusters_cursos.csv", index=False)
    print("Clusters de cursos não transversais salvos em 'clusters_cursos.csv'.")

   
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        x=df_clusters["Componente 1"], y=df_clusters["Componente 2"],
        hue=df_clusters["Cluster"], palette="viridis", s=100
    )
    plt.title("Clusters dos Cursos Não Transversais")
    plt.xlabel("Componente Principal 1")
    plt.ylabel("Componente Principal 2")
    plt.legend(title="Grupo")
    plt.grid(True)
    plt.show()

print("Processo concluído com sucesso!")
