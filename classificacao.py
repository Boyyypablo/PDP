from scraping import obter_titulos_cursos  
from processamento import calcular_similaridade, obter_descricoes_cursos

def recomendar_curso():
    
    titulos_cursos_site = obter_titulos_cursos()  
    cursos_banco = obter_descricoes_cursos()  

    if not titulos_cursos_site or not cursos_banco:
        print("Erro: Não foi possível obter cursos do site ou do banco.")
        return None, None

    similaridades = calcular_similaridade(" ".join(titulos_cursos_site), cursos_banco)

    indice_melhor_curso = similaridades.argmax()
    melhor_similaridade = similaridades[indice_melhor_curso]

    return titulos_cursos_site[indice_melhor_curso], melhor_similaridade

if __name__ == "__main__":
    melhor_curso, similaridade = recomendar_curso()
    
    if melhor_curso:
        print(f"Melhor curso recomendado: {melhor_curso}")
        print(f"Similaridade: {similaridade:.2f}")
    else:
        print("Nenhum curso recomendado encontrado.")
