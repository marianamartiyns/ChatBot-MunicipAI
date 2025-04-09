import pandas as pd
import requests
from bs4 import BeautifulSoup
import unicodedata

# =================== FAZ O SCRAPING DOS DADOS DO IBGE ===================
# https://www.ibge.gov.br/cidades-e-estados/PB.html

estados = [
    'ac', 'al', 'ap', 'am', 'ba', 'ce', 'df', 'es', 'go', 'ma',
    'mt', 'ms', 'mg', 'pa', 'pb', 'pr', 'pe', 'pi', 'rj', 'rn',
    'rs', 'ro', 'rr', 'sc', 'sp', 'se', 'to'
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def normalizar_texto(texto: str) -> str:
    """Remove acentos e espaços extras do texto."""
    texto = unicodedata.normalize('NFKD', texto)
    texto = ''.join([c for c in texto if not unicodedata.combining(c)])
    return texto.strip()

def extrair_indicadores_estado(uf: str) -> dict:
    """
    Faz scraping da página de um estado no site do IBGE e extrai os indicadores disponíveis.
    """
    estado_url = f'https://www.ibge.gov.br/cidades-e-estados/{uf}.html'
    
    try:
        response = requests.get(estado_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        return {"UF": uf.upper(), "erro": f"Falha ao acessar página: {e}"}

    soup = BeautifulSoup(response.content, 'html.parser')
    indicadores = soup.select('.indicador')

    dados = {}
    for ind in indicadores:
        label = ind.select_one('.ind-label')
        valor = ind.select_one('.ind-value')
        if label and valor:
            chave = normalizar_texto(label.text)
            dados[chave] = valor.text.strip()

    dados['UF'] = uf.upper()
    return dados

def coletar_indicadores_estaduais() -> pd.DataFrame:
    """
    Coleta os indicadores de todos os estados e retorna como DataFrame.
    """
    dados = [extrair_indicadores_estado(uf) for uf in estados]
    return pd.DataFrame(dados)

def carregar_dados_estaduais(cod_estado: str) -> dict:
    """
    Recebe o código IBGE (ex: '31' para Minas Gerais) e retorna os dados via scraping do IBGE.
    """
    cod_to_uf = {
        '12': 'ac', '27': 'al', '16': 'ap', '13': 'am', '29': 'ba', '23': 'ce', '53': 'df',
        '32': 'es', '52': 'go', '21': 'ma', '51': 'mt', '50': 'ms', '31': 'mg', '15': 'pa',
        '25': 'pb', '41': 'pr', '26': 'pe', '22': 'pi', '33': 'rj', '24': 'rn', '43': 'rs',
        '11': 'ro', '14': 'rr', '42': 'sc', '35': 'sp', '28': 'se', '17': 'to'
    }

    uf = cod_to_uf.get(cod_estado.zfill(2))
    if not uf:
        return {"erro": "Código de estado inválido."}

    return extrair_indicadores_estado(uf)
