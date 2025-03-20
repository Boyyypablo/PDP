import pandas as pd
from sqlalchemy import create_engine

def obter_dados_postgres(query):
    engine = create_engine('postgresql+psycopg2://postgres:12345@localhost:5432/pdp')
    df = pd.read_sql(query, engine)
    return df

if __name__ == "__main__":
    query = "SELECT * FROM minha_tabela"
    df = obter_dados_postgres(query)
    print(df.head())
