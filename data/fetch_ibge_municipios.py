import requests
from bs4 import BeautifulSoup
import unicodedata
import re

# =================== FAZ O SCRAPING DOS DADOS DO IBGE ===================
# https://www.ibge.gov.br/cidades-e-estados/rn/acu.html

def slugify(texto: str) -> str:
    texto = unicodedata.normalize('NFKD', texto)
    texto = ''.join([c for c in texto if not unicodedata.combining(c)])
    texto = re.sub(r'[^a-zA-Z0-9\s-]', '', texto)
    return texto.lower().replace(' ', '-')

def extrair_dados_municipio(uf: str, municipio: str) -> dict:
    """
    Acessa a página do município no site do IBGE e extrai os indicadores principais.
    """
    slug_mun = slugify(municipio)
    url = f'https://www.ibge.gov.br/cidades-e-estados/{uf.lower()}/{slug_mun}.html'

    
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        return {"erro": f"Erro ao acessar página: {e}", "url": url}

    soup = BeautifulSoup(response.content, 'html.parser')
    indicadores = soup.select('.indicador')

    dados = {}
    for ind in indicadores:
        label = ind.select_one('.ind-label')
        valor = ind.select_one('.ind-value')
        if label and valor:
            chave = unicodedata.normalize('NFKD', label.text).strip()
            chave = re.sub(r'\s+', ' ', chave)
            dados[chave] = valor.text.strip()
    
    dados['Município'] = municipio
    dados['UF'] = uf.upper()
    dados['Fonte'] = url
    return dados
