# Instale antes essas dependências:
# pip install selenium webdriver-manager sentence-transformers pandas beautifulsoup4 torch

import os
os.environ['WDM_SSL_VERIFY'] = '0'  # Ignorar SSL para webdriver-manager

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup
import pandas as pd
from sentence_transformers import SentenceTransformer, util

# Configuração do Chrome headless
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--ignore-certificate-errors')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

base_url = "https://www.escolavirtual.gov.br/catalogo"

# Texto descritivo do setor CGL
cgl_profile = """
O setor de Coordenação-Geral de Licitações e Contratos (CGL) é responsável por gerenciar processos de licitações,
contratos, compras públicas, gestão de contratos, conformidade com normas legais, e gestão de fornecedores.
Profissionais deste setor precisam de conhecimentos em legislação, gestão de contratos, processos licitatórios,
gestão de riscos, e ética na administração pública.
"""

# Modelo Sentence Transformer
model = SentenceTransformer('all-MiniLM-L6-v2')
cgl_embedding = model.encode(cgl_profile, convert_to_tensor=True)

cursos_detalhes = []

# Função para extrair links dos cursos na página atual
def extrair_links_cursos():
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    return [a['href'] for a in soup.select('h3.card-title a')]

# Abrir a primeira página do catálogo
driver.get(base_url)
time.sleep(3)

pagina_atual = 1
total_cursos = 0

while True:
    print(f"Processando página {pagina_atual}...")
    links_cursos = extrair_links_cursos()

    for link in links_cursos:
        driver.get(link)
        time.sleep(2)
        
        curso_soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        titulo = curso_soup.find('h1').text.strip() if curso_soup.find('h1') else "Sem título"
        conteudo = curso_soup.select_one("dd.columns.rich-text")
        descricao_curso = conteudo.get_text(separator=" ", strip=True) if conteudo else "Sem descrição disponível"

        embedding_curso = model.encode(descricao_curso, convert_to_tensor=True)
        similaridade = util.pytorch_cos_sim(cgl_embedding, embedding_curso).item()

        cursos_detalhes.append({
            "Título": titulo,
            "Link": link,
            "Descrição": descricao_curso,
            "Similaridade com CGL": similaridade
        })

        total_cursos += 1
        print(f"Curso '{titulo}' analisado. Similaridade: {similaridade:.4f}")

    # Verificar se há próxima página
    try:
        driver.get(f"{base_url}?page={pagina_atual+1}")
        time.sleep(3)
        
        # Condição para parar se a página não existir ou estiver vazia
        if "Nenhum curso encontrado" in driver.page_source or not extrair_links_cursos():
            break
        else:
            pagina_atual += 1

    except Exception as e:
        print("Erro ao acessar próxima página ou fim das páginas.")
        break

driver.quit()

# Criar DataFrame dos cursos analisados
df_cursos = pd.DataFrame(cursos_detalhes)

# Ordenar por similaridade e obter top 10
df_top10 = df_cursos.sort_values(by="Similaridade com CGL", ascending=False).head(10)

# Exibir resultado
print("\nTop 10 cursos recomendados para o setor CGL:")
print(df_top10[['Título', 'Similaridade com CGL', 'Link']])

# Salvar o resultado
df_top10.to_excel("top10_cursos_recomendados_CGL.xlsx", index=False)
