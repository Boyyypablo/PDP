import pandas as pd
from sqlalchemy import create_engine, text
from sentence_transformers import SentenceTransformer, util


DB_USER = "postgres"
DB_PASSWORD = "12345"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "pdp"

engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")


modelo = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def atualizar_tematica3(caminho_arquivo):
   

    df_csv = pd.read_csv(caminho_arquivo, encoding="utf-8", delimiter=";")

   
    df_csv["nome_curso"] = df_csv["nome_curso"].str.strip().str.lower()
    df_csv["eixos_tematicos"] = df_csv["eixos_tematicos"].str.strip()

   
    df_db = pd.read_sql("SELECT id, tematica_2 FROM minha_tabela", engine)
    df_db["tematica_2"] = df_db["tematica_2"].str.strip().str.lower()

    emb_tematicas = modelo.encode(df_db["tematica_2"].tolist(), convert_to_tensor=True)
    emb_cursos = modelo.encode(df_csv["nome_curso"].tolist(), convert_to_tensor=True)

   
    tematica3_dict = {}

    
    for i, emb_tematica in enumerate(emb_tematicas):
        similaridades = util.pytorch_cos_sim(emb_tematica, emb_cursos)[0]
        max_sim_index = similaridades.argmax().item()
        melhor_similaridade = similaridades[max_sim_index].item()

       
        if melhor_similaridade > 0.40:  
            tematica3_dict[int(df_db.loc[i, "id"])] = df_csv.loc[max_sim_index, "eixos_tematicos"]
        else:
            tematica3_dict[int(df_db.loc[i, "id"])] = None  

    
    print("\n🔍 Visualizando correspondências antes do update:")
    for k, v in tematica3_dict.items():
        print(f"ID: {k} -> {v}")

    
    with engine.connect() as conn:
        for id_value, eixo_tematico in tematica3_dict.items():
            if eixo_tematico:  
                query = text("""
                    UPDATE minha_tabela
                    SET tematica_3 = :tematica_3
                    WHERE id = :id
                """)
                conn.execute(query, {"tematica_3": eixo_tematico, "id": int(id_value)})  

        conn.commit()

    print("\n✅ Coluna 'tematica_3' atualizada com sucesso!")

if __name__ == "__main__":
    caminho_arquivo = r"C:\Users\pablo.basilio\Documents\PDP projeto\eixostematicos.csv"
    atualizar_tematica3(caminho_arquivo)
