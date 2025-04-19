import pandas as pd
import requests
from bs4 import BeautifulSoup
import unicodedata
import re
import json
import os

# ==================== DADOS LOCAIS (estados.json e municipios.json) ====================

with open("backend/data/estados.json", encoding="utf-8") as f:
    ESTADOS = json.load(f)

with open("backend/data/municipios.json", encoding="utf-8") as f:
    MUNICIPIOS = json.load(f)

# ==================== FUNÇÃO DE NORMALIZAÇÃO ====================

def normalizar(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("ASCII").lower().strip()

# ==================== FUNÇÕES AUXILIARES DE LOCALIZAÇÃO ====================

def get_sigla_uf_por_codigo(cod_estado: str) -> str:
    estado = ESTADOS.get(str(cod_estado).zfill(2))
    return estado["sigla"].lower() if estado else None

def get_uf_por_nome(nome_estado: str) -> str:
    nome_normalizado = normalizar(nome_estado)
    for est in ESTADOS.values():
        if est.get("nome_normalizado") == nome_normalizado:
            return est["sigla"].lower()
    return None

def get_estado_por_sigla(sigla: str) -> str:
    for cod, est in ESTADOS.items():
        if est["sigla"].lower() == sigla.lower():
            return cod
    return None

def get_uf_e_nome_municipio(codigo_municipio: str) -> tuple:
    mun = MUNICIPIOS.get(str(codigo_municipio))
    if not mun:
        return None, None
    cod_estado = mun["cod_estado"]
    uf = get_sigla_uf_por_codigo(cod_estado)
    return uf, mun["nome"]

# ==================== PARÂMETROS DE SCRAPING ====================

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# ==================== SCRAPING ESTADUAL ====================

def extrair_indicadores_estado(uf: str) -> dict:
    url = f'https://www.ibge.gov.br/cidades-e-estados/{uf}.html'
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        return {"UF": uf.upper(), "erro": f"Erro ao acessar página: {e}"}

    soup = BeautifulSoup(response.content, 'html.parser')
    indicadores = soup.select('.indicador')

    dados = {}
    for ind in indicadores:
        label = ind.select_one('.ind-label')
        valor = ind.select_one('.ind-value')
        if label and valor:
            chave = normalizar(label.text)
            dados[chave] = valor.text.strip()

    dados['UF'] = uf.upper()
    dados['Fonte'] = url
    return dados

def carregar_dados_estaduais(cod_estado: str) -> dict:
    uf = get_sigla_uf_por_codigo(cod_estado)
    if not uf:
        return {"erro": "Código de estado inválido."}
    return extrair_indicadores_estado(uf)

def coletar_indicadores_estaduais() -> pd.DataFrame:
    dados = [extrair_indicadores_estado(uf["sigla"].lower()) for uf in ESTADOS.values()]
    return pd.DataFrame(dados)

# ==================== SCRAPING MUNICIPAL ====================

def slugify(texto: str) -> str:
    texto = normalizar(texto)
    texto = re.sub(r'[^a-z0-9\s-]', '', texto)
    return texto.replace(' ', '-')

def extrair_dados_municipio(cod_municipio: str) -> dict:
    uf, nome_mun = get_uf_e_nome_municipio(cod_municipio)
    if not uf or not nome_mun:
        return {"erro": "Código de município inválido ou não encontrado."}

    slug_mun = slugify(nome_mun)
    url = f'https://www.ibge.gov.br/cidades-e-estados/{uf}/{slug_mun}.html'

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
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
            chave = normalizar(label.text)
            dados[chave] = valor.text.strip()

    dados['Município'] = nome_mun
    dados['UF'] = uf.upper()
    dados['Fonte'] = url
    return dados
