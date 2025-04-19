import os
import json
import requests
import pandas as pd
import unicodedata
from sidrapy import get_table

# ==================== CARREGAMENTO DE DADOS ====================

with open("backend/data/estados.json", encoding="utf-8") as f:
    ESTADOS = json.load(f)

with open("backend/data/municipios.json", encoding="utf-8") as f:
    MUNICIPIOS = json.load(f)

# ==================== NORMALIZAÇÃO DE TEXTO ====================

def normalizar(texto):
    return unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("ASCII").lower().strip()

# ==================== INDICADORES ====================

indicadores_municipios = {
    "População Total": {
        "tabela": 6579,
        "variável": 9324,
        "nível_territorial": "municipal"
    },
    "Municípios com serviço de abastecimento de água por rede geral de distribuição em funcionamento (Unidades)": {
        "tabela": 7462, "variável": 1399, "nível_territorial": "municipal"
    },
    "Municípios com serviço de esgotamento sanitário (Unidades)": {
        "tabela": 7461, "variável": 1388, "nível_territorial": "municipal"
    },
    "Municípios com serviço de esgotamento sanitário por rede coletora em funcionamento (Unidades)": {
        "tabela": 7472, "variável": 1501, "nível_territorial": "municipal"
    },
    "Municípios com serviço de abastecimento de água por rede geral de distribuição (Unidades)": {
        "tabela": 7460, "variável": 1379, "nível_territorial": "municipal"
    },
}

indicadores_estados = {
    "População residente estimada (Pessoas)": {
        "tabela": 6579, "variável": 9325, "nível_territorial": "estadual"
    },
    "Produto Interno Bruto a preços correntes (Mil Reais)": {
        "tabela": 5938, "variável": 1985, "nível_territorial": "estadual"
    },
    "PIB per capita (Mil Reais)": {
        "tabela": 5938, "variável": 593, "nível_territorial": "estadual"
    },
    "Rendimento médio mensal per capita em domicílios com celular (Reais)": {
        "tabela": 7412, "nível_territorial": "estadual"
    },
    "Rendimento médio mensal real domiciliar per capita em domicílios que havia utilização da Internet (Reais)": {
        "tabela": 7419, "variável": 1257, "nível_territorial": "estadual"
    },
    "Pessoas de 10 anos ou mais cujo domicílio não possui morador que recebeu rendimento do Bolsa Família (Mil)": {
        "tabela": 7448, "variável": 1244, "nível_territorial": "estadual"
    },
    "Domicílios com algum morador que recebeu Benefício de Prestação Continuada (Mil)": {
        "tabela": 7451, "nível_territorial": "estadual"
    }
}

# ==================== UTILITÁRIOS LOCAIS ====================

def get_nome_estado(cod_estado):
    return ESTADOS.get(str(cod_estado), {}).get("nome")

def get_sigla_estado(cod_estado):
    return ESTADOS.get(str(cod_estado), {}).get("sigla")

def get_cod_estado_por_nome(nome_estado):
    nome_norm = normalizar(nome_estado)
    for cod, info in ESTADOS.items():
        if info.get("nome_normalizado") == nome_norm:
            return cod
    return None

def get_cod_municipio_por_nome(nome_mun):
    nome_norm = normalizar(nome_mun)
    for cod, info in MUNICIPIOS.items():
        if info.get("nome_normalizado") == nome_norm:
            return cod
    return None

def get_municipios_por_estado(cod_estado):
    return {k: v["nome"] for k, v in MUNICIPIOS.items() if v["cod_estado"] == str(cod_estado)}

# ==================== COLETA E TRATAMENTO ====================

def formata_valor(valor):
    try:
        num = float(valor)
        if 0 < num < 1:
            return f"{num * 100:.2f}%"
        elif valor.endswith("%"):
            return valor
        else:
            return f"{num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return valor

def tratar_dados(df):
    df = df.drop_duplicates()
    df = df[df["Valor"] != "-"]
    df["Ano"] = pd.to_numeric(df["Ano"], errors="coerce")
    df = df[df["Ano"].notna()]
    df = df.sort_values(by="Ano", ascending=False)

    if "D1N" in df.columns:
        for pref in ["Total", "Município", "Estado", "Brasil"]:
            df_filtrado = df[df["D1N"].str.contains(pref, case=False, na=False)]
            if not df_filtrado.empty:
                df = df_filtrado
                break

    df["Valor"] = df["Valor"].apply(formata_valor)
    return df

def selecionar_indicadores_por_local(codigo_local):
    return indicadores_municipios if len(codigo_local) == 7 else indicadores_estados

def coletar_dados_local(codigo_local):
    dfs = []
    indicadores = selecionar_indicadores_por_local(codigo_local)

    for nome_indicador, info in indicadores.items():
        tabela = info["tabela"]
        variavel = info.get("variavel")
        nivel = "n6" if len(codigo_local) == 7 else "n3"

        url = f"https://apisidra.ibge.gov.br/values/t/{tabela}/{nivel}/{codigo_local}/p/last"
        if variavel:
            url += f"/v/{variavel}"

        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            print(f"[Erro] Tabela {tabela}: código {response.status_code}")
            continue

        try:
            dados = response.json()
            colunas = list(dados[0].values())
            registros = [list(item.values()) for item in dados[1:]]
            df = pd.DataFrame(registros, columns=colunas)
            df["indicador"] = nome_indicador
            df = tratar_dados(df)
            dfs.append(df)
        except Exception as e:
            print(f"[Erro JSON] {nome_indicador}: {e}")

    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

# ==================== FERRAMENTAS PARA AGENTE ====================

def responder_coleta_sidra(pergunta: str) -> str:
    pergunta_norm = normalizar(pergunta)
    cod = get_cod_municipio_por_nome(pergunta_norm) or get_cod_estado_por_nome(pergunta_norm)

    if not cod:
        return "Não identifiquei a localidade. Tente informar o nome exato de um município ou estado."

    df = coletar_dados_local(cod)
    if df.empty:
        return "Nenhum dado encontrado."

    resumo = []
    for ind in df["indicador"].unique():
        try:
            linha = df[df["indicador"] == ind].iloc[0]
            resumo.append(f"- **{ind}**: {linha['Valor']} ({linha['Ano']})")
        except:
            continue
    return "\n".join(resumo) if resumo else "Não consegui resumir os dados."

def consultar_sidra_chatbot(pergunta: str) -> str:
    pergunta_norm = normalizar(pergunta)
    cod = get_cod_municipio_por_nome(pergunta_norm) or get_cod_estado_por_nome(pergunta_norm)
    if not cod:
        return "Localidade não reconhecida."

    if "pib" in pergunta_norm:
        tabela, variaveis = "2938", "37"
    elif "populacao" in pergunta_norm:
        tabela, variaveis = "6579", "93"
    elif "leite" in pergunta_norm:
        tabela, variaveis = "1419", "214"
    else:
        return "Indicador não reconhecido."

    df = consultar_sidra(tabela, cod, variaveis)
    if isinstance(df, str):
        return f"⚠️ {df}"
    if df.empty:
        return "Nenhum dado encontrado."

    try:
        linha = df.sort_values(by="Ano", ascending=False).iloc[0]
        valor = linha["Valor"]
        ano = linha["Ano"]
        return f"📊 Valor: **{valor}** ({ano})"
    except Exception as e:
        return f"Erro ao interpretar o dado: {e}"

def consultar_sidra(tabela, codigo_local, variaveis=None):
    nivel = "n6" if len(codigo_local) == 7 else "n3"
    url = f"https://apisidra.ibge.gov.br/values/t/{tabela}/{nivel}/{codigo_local}/p/last"
    if variaveis:
        url += f"/v/{variaveis}"

    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code != 200:
        return f"Erro ao consultar tabela {tabela} (código {response.status_code})"

    try:
        dados = response.json()
        colunas = list(dados[0].values())
        registros = [list(item.values()) for item in dados[1:]]
        return pd.DataFrame(registros, columns=colunas)
    except Exception as e:
        return f"Erro ao processar JSON: {e}"
