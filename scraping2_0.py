import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, text
import pandas as pd
from sentence_transformers import SentenceTransformer, util


DB_USER = "postgres"
DB_PASSWORD = "12345"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "pdp"

engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")


modelo = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')


URL_BASE = "https://www.escolavirtual.gov.br/catalogo?page={}"
URL_CURSO = "https://www.escolavirtual.gov.br"

def obter_titulos_e_conteudos():
   
    cursos_info = []
    pagina = 1

    while True:
        resposta = requests.get(URL_BASE.format(pagina))
        if resposta.status_code != 200:
            print(f"Erro ao acessar a página {pagina}: {resposta.status_code}")
            break

        soup = BeautifulSoup(resposta.text, 'html.parser')

        cursos = soup.select('.card-body')
        if not cursos:
            print(f"Fim da paginação. Última página: {pagina - 1}")
            break  

        for curso in cursos:
            titulo = curso.select_one('.card-title')
            link = curso.select_one('a')

            if titulo and link:
                titulo_texto = titulo.get_text(strip=True) if titulo else ""
                link_curso = link['href']
                
                
                if not link_curso.startswith("http"):  
                    link_curso = URL_CURSO + link_curso  

                
                conteudo = obter_conteudo_programatico(link_curso)

                cursos_info.append({
                    "titulo": titulo_texto,
                    "conteudo": conteudo
                })

        print(f"Página {pagina} - Cursos extraídos: {len(cursos)}")
        pagina += 1  

    return cursos_info


def obter_conteudo_programatico(url_curso):
    
    try:
        resposta = requests.get(url_curso)
        if resposta.status_code != 200:
            return "Desconhecido"

        soup = BeautifulSoup(resposta.text, 'html.parser')

        conteudo_elementos = soup.select(".box-conteudo-programatico li")
        conteudo = " ".join([modulo.get_text(strip=True) for modulo in conteudo_elementos])
        
        return conteudo if conteudo else "Não Informado"

    except Exception as e:
        print(f"Erro ao acessar {url_curso}: {e}")
        return "Erro"


def calcular_similaridade(texto, referencias):
    
    if not referencias:
        return 0, ""

    
    texto = texto if isinstance(texto, str) else ""
    referencias = [ref if isinstance(ref, str) else "" for ref in referencias]

    
    embeddings_texto = modelo.encode(texto, convert_to_tensor=True)
    embeddings_referencias = modelo.encode(referencias, convert_to_tensor=True)

    
    similaridades = util.pytorch_cos_sim(embeddings_texto, embeddings_referencias)[0]
    
   
    indice_max = similaridades.argmax().item()
    
    return similaridades[indice_max].item(), referencias[indice_max]


def atualizar_tabela_postgres():
   
    cursos = obter_titulos_e_conteudos()

    df = pd.read_sql("SELECT id, o_que_nao_se_sabe_fazer_ou_nao_ser, recorte_do_tema_geral FROM minha_tabela", engine)

    with engine.connect() as conn:
        for _, row in df.iterrows():
            melhor_sim, melhor_curso = calcular_similaridade(
                row["o_que_nao_se_sabe_fazer_ou_nao_ser"],
                [curso["titulo"] + " " + curso["conteudo"] for curso in cursos]
            )

            
            if melhor_sim < 0.30:
                melhor_sim, melhor_curso = calcular_similaridade(
                    row["recorte_do_tema_geral"],
                    [curso["titulo"] + " " + curso["conteudo"] for curso in cursos]
                )

            query = text("""
    UPDATE minha_tabela
    SET tematica_2 = :tematica
    WHERE id = :id;
""")

            conn.execute(query, {"tematica": melhor_curso, "id": row["id"]})

        conn.commit()

    print("Coluna 'Tematica 2.0' atualizada com sucesso!")



if __name__ == "__main__":
    atualizar_tabela_postgres()
