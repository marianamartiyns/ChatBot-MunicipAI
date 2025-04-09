import os 
import requests
import pandas as pd

# ============= NO MOMENTO, NÃO ESTÁ PEGANDO
# === Indicadores por tema ===

indicadores_municipios = {

    "População Total": {
        "tabela": 6579,
        "variável": 9324,
        "nível_territorial": "municipal"
    },

    "Municípios com serviço de abastecimento de água por rede geral de distribuição em funcionamento (Unidades)": { #2017
        "tabela": 7462, 
        "variável": 1399,
        "nível_territorial": "municipal"
    },

    "Municípios com serviço de esgotamento sanitário (Unidades)": {
        "tabela": 7461, # 2017
        "variável": 1388,
        "nível_territorial": "municipal"
    },

    "Municípios com serviço de esgotamento sanitário por rede coletora em funcionamento (Unidades)": {
        "tabela": 7472, # 2017
        "variável": 1501,
        "nível_territorial": "municipal"
    },

    "Municípios com serviço de abastecimento de água por rede geral de distribuição (Unidades)": {
        "tabela": 7460, # 2017
        "variável": 1379,
        "nível_territorial": "municipal"
    },
}


indicadores_estados = {

    "População residente estimada (Pessoas)": {
        "tabela": 6579,
        "variável": 9325,
        "nível_territorial": "estadual"
    },

    "Produto Interno Bruto a preços correntes (Mil Reais)": {
        "tabela": 5938,
        "variável": 1985,
        "nível_territorial": "estadual"
    },

    "PIB per capita (Mil Reais)": {
        "tabela": 5938,
        "variável": 593,
        "nível_territorial": "estadual"
    },

    "Rendimento médio mensal per capita em domicílios com celular (Reais)": {
        "tabela": 7412,
        "nível_territorial": "estadual"
    },

    "Rendimento médio mensal real domiciliar per capita em domicílios que havia utilização da Internet (Reais)": {
        "tabela": 7419,
        "variável": 1257,
        "nível_territorial": "estadual"
    },

    "Pessoas de 10 anos ou mais de idade cujo domicílio não possui morador que recebeu rendimento do Programa Bolsa Família (Mil pessoas)": { # 2023
        "tabela": 7448,
        "variável": 1244,
        "nível_territorial": "estadual"
    },

    "Domicílios em que algum morador do domicílio recebeu rendimento do Benefício de Prestação Continuada (Mil unidades)": {
        "tabela": 7451,
        "nível_territorial": "estadual"
    }
}


# === Carregar lista de municípios ===
def carregar_municipios(path_txt):
    municipios = []
    with open(path_txt, 'r', encoding='utf-8') as f:
        for linha in f:
            nome, codigo = linha.strip().split(',')
            municipios.append({"nome": nome.strip(), "codigo": codigo.strip()})
    return municipios

# === Função para formatar valores (exibe percentuais se o valor estiver entre 0 e 1) ===
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

# === Função para tratar os dados: remove repetições, valores indesejados e formata os valores ===
def tratar_dados(df):
    df = df.drop_duplicates()
    df = df[df["Valor"] != "-"]
    df["Ano"] = pd.to_numeric(df["Ano"], errors="coerce")
    df = df[df["Ano"].notna()]
    df = df.sort_values(by="Ano", ascending=False)

    # Filtra apenas os valores principais se houver múltiplas linhas por ano
    if "D1N" in df.columns:
        descritores = df["D1N"].unique().tolist()
        preferidos = ["Total", "Valor total", "Município", "Estado", "Brasil"]
        for pref in preferidos:
            df_filtrado = df[df["D1N"].str.contains(pref, case=False, na=False)]
            if not df_filtrado.empty:
                df = df_filtrado
                break

    df["Valor"] = df["Valor"].apply(formata_valor)
    return df

# === Função para selecionar indicadores por local ===
def selecionar_indicadores_por_local(codigo_local):
    if len(codigo_local) == 7:  # Código de município
        return indicadores_municipios
    elif len(codigo_local) == 2:  # Código de estado
         return indicadores_estados
    else:
        raise ValueError("Código local inválido.")
dfs = []

# === Coleta dados de qualquer local (município ou estado) ===
def coletar_dados_local(codigo_local):
    indicadores = selecionar_indicadores_por_local(codigo_local)
    
    for nome_indicador, info in indicadores.items():
        tabela = info["tabela"]
        variavel = info.get("variavel")

        nivel = "n6" if len(codigo_local) == 7 else "n3"

        url = f"https://apisidra.ibge.gov.br/values/t/{tabela}/{nivel}/{codigo_local}/p/last"
        if variavel:
            url += f"/v/{variavel}"

        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"[Erro] Tabela {tabela}: código {response.status_code}")
            print("Resposta:", response.text[:200])
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
            print(f"[Erro JSON] Indicador {nome_indicador}: {e}")
            print("Resposta:", response.text[:200])

    if dfs:
        return pd.concat(dfs, ignore_index=True)
    else:
        print("Nenhum dado coletado.")
        return pd.DataFrame()

# === Exibe resumo dos dados de forma limpa ===
def mostrar_resumo(df, nome_local):
    print(f"\n📊 Indicadores de {nome_local}")
    if df.empty:
        print("⚠️ Nenhum dado disponível.")
        return

    for ind in df["indicador"].unique():
        df_ind = df[df["indicador"] == ind].copy()
        colunas_base = ["Ano"]
        colunas_descritoras = [col for col in df_ind.columns if col.startswith("D") and col.endswith("N")]
        colunas_mostrar = colunas_base + colunas_descritoras + ["Valor"]

        print(f"\n🔹 {ind}")
        print(df_ind[colunas_mostrar].drop_duplicates().head(5))

def get_tabelas_disponiveis():
    tabelas = {}

    for nome, info in indicadores_municipios.items():
        tabelas[str(info["tabela"])] = nome

    for nome, info in indicadores_estados.items():
        tabelas[str(info["tabela"])] = nome

    return tabelas
