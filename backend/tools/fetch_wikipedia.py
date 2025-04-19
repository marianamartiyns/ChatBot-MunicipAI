import requests
from bs4 import BeautifulSoup
import re
import json
import os
import time
import unicodedata

# ==================== NORMALIZAÇÃO ====================

def normalizar(texto):
    return unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("ASCII").strip()

def limpar_texto(texto):
    if not texto:
        return ""
    texto = re.sub(r"\[.*?\]", "", texto)  # Remove referências [1]
    texto = texto.replace('\xa0', ' ')
    return texto.strip()

# ==================== EXTRAÇÃO ====================

def extrair_infobox(soup):
    infobox = soup.find("table", {"class": "infobox"})
    dados = {}
    if not infobox:
        return dados

    linhas = infobox.find_all("tr")
    for linha in linhas:
        th = linha.find("th")
        td = linha.find("td")
        if th and td:
            chave = limpar_texto(th.text).lower()
            valor = limpar_texto(td.text)
            dados[chave] = valor
    return dados

def extrair_secoes_relevantes(soup):
    dados_adicionais = {
        "educacao": "",
        "saneamento": "",
        "rodovias": ""
    }

    secoes = soup.find_all(['h2', 'h3'])
    for secao in secoes:
        titulo = secao.text.lower()
        proximo = secao.find_next_sibling()
        conteudo = []

        while proximo and proximo.name not in ['h2', 'h3']:
            if proximo.name == 'p':
                conteudo.append(limpar_texto(proximo.text))
            proximo = proximo.find_next_sibling()

        texto = " ".join(conteudo)
        if "educa" in titulo:
            dados_adicionais["educacao"] = texto
        elif "saneamento" in titulo:
            dados_adicionais["saneamento"] = texto
        elif "rodovia" in titulo or "transport" in titulo:
            dados_adicionais["rodovias"] = texto

    return dados_adicionais

# ==================== FUNÇÃO PRINCIPAL DE COLETA ====================

def coletar_dados_wikipedia(nome: str, tipo: str = "municipio") -> dict:
    nome = nome.strip()
    nome_formatado = nome.replace(" ", "_")

    if tipo == "estado":
        if nome.startswith("Rio Grande"):
            nome_formatado = "Estado_do_" + nome_formatado
        else:
            nome_formatado = "Estado_de_" + nome_formatado

    url = f"https://pt.wikipedia.org/wiki/{nome_formatado}"

    response = requests.get(url)
    if response.status_code != 200:
        return {"erro": f"Página não encontrada ({response.status_code})", "fonte": url}

    soup = BeautifulSoup(response.content, 'html.parser')
    dados = extrair_infobox(soup)
    dados.update(extrair_secoes_relevantes(soup))
    dados["fonte"] = url
    return dados

# ==================== CARGA DE DADOS ====================

def carregar_json(caminho):
    with open(caminho, 'r', encoding='utf-8') as f:
        return json.load(f)

# ==================== EXECUÇÃO EM LOTE ====================

def main():
    caminho_estados = os.path.join('backend', 'data', 'estados.json')
    caminho_municipios = os.path.join('backend', 'data', 'municipios.json')

    estados = carregar_json(caminho_estados)
    municipios = carregar_json(caminho_municipios)

    dados_municipios = {}
    dados_estados = {}

    print("\n=== Coletando dados dos MUNICÍPIOS ===")
    for cod_municipio, info in municipios.items():
        nome = info.get("nome")
        try:
            print(f"🔎 Município: {nome}")
            dados = coletar_dados_wikipedia(nome, tipo="municipio")
            dados_municipios[cod_municipio] = dados
        except Exception as e:
            print(f"⚠️ Erro em {nome}: {e}")
        time.sleep(1)

    print("\n=== Coletando dados dos ESTADOS ===")
    for cod_estado, info in estados.items():
        nome_estado = info.get("nome")
        try:
            print(f"🗺️ Estado: {nome_estado}")
            dados = coletar_dados_wikipedia(nome_estado, tipo="estado")
            dados_estados[cod_estado] = dados
        except Exception as e:
            print(f"⚠️ Erro em {nome_estado}: {e}")
        time.sleep(1)

    print(f"\n✅ Coleta finalizada: {len(dados_municipios)} municípios e {len(dados_estados)} estados.")
    return dados_municipios, dados_estados
