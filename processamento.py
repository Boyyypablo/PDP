from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
from conexao import obter_dados_postgres
from scraping import obter_titulos_cursos  

nlp = spacy.load("pt_core_news_sm")

def preprocessar(texto):
   
    if not isinstance(texto, str):
        return ""
    doc = nlp(texto.lower())
    tokens = [token.lemma_ for token in doc if not token.is_stop and token.is_alpha]
    return " ".join(tokens)

def calcular_similaridade(texto_site, textos_cursos):
   
    textos = [preprocessar(texto_site)] + [preprocessar(curso) for curso in textos_cursos]
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(textos)
    return cosine_similarity(X[0], X[1:])[0]

def obter_descricoes_cursos():
    
    query = "SELECT o_que_nao_se_sabe_fazer_ou_nao_ser FROM minha_tabela"
    df = obter_dados_postgres(query)
    return df['o_que_nao_se_sabe_fazer_ou_nao_ser'].dropna().tolist()

if __name__ == "__main__":
    cursos_site = obter_titulos_cursos()
    
    descricoes_postgres = obter_descricoes_cursos()

   
    for titulo in cursos_site:
        similaridades = calcular_similaridade(titulo, descricoes_postgres)
        melhor_indice = similaridades.argmax() 
        print(f"Curso do site: {titulo}")
        print(f"Melhor correspondência no banco: {descricoes_postgres[melhor_indice]}")
        print(f"Similaridade: {similaridades[melhor_indice]:.2f}\n")
