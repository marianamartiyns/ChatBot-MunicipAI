import os
import requests
import pandas as pd

# === Indicadores disponíveis para municípios ===
indicadores_municipios = {
    "populacao_total": {"tabela": 6579},
    "pib_municipal": {"tabela": 5938}
    # "mortalidade_infantil": {"tabela": 1419}
}

# === Indicadores disponíveis apenas para estados (ou Brasil) ===
indicadores_estados = {
    "densidade_demografica": {"tabela": 6579},
    "populacao_urbana_rural": {"tabela": 6579},

    "renda_media_domiciliar": {"tabela": 5128},
    # "percentual_renda_ate_meio_salario": {"tabela": 6411},
    "atividade_economica_setores": {"tabela": 5938},
    
    "agua_encanada": {"tabela": 7412},
    "esgoto_sanitario": {"tabela": 7412},
    "coleta_lixo": {"tabela": 7412},
    "energia_eletrica": {"tabela": 7412},

    "alfabetizacao": {"tabela": 7473},
    "escolaridade_fundamental_medio_superior": {"tabela": 7473},
    "frequencia_escolar": {"tabela": 7473},

    # "cobertura_prenatal": {"tabela": 8183},
    "estabelecimentos_saude": {"tabela": 3366},

    "taxa_desocupacao": {"tabela": 4093},
    "proporcao_ocupados": {"tabela": 4093},
    # "tipo_ocupacao": {"tabela": 4093},

    "receita_despesa_publica": {"tabela": 7789},
    # "idhm": {"tabela": 6288},
    # "indice_gini": {"tabela": 6399}
}

# === Carregar lista de municípios ===
def carregar_municipios(path_txt):
    municipios = []
    with open(path_txt, 'r', encoding='utf-8') as f:
        for linha in f:
            nome, codigo = linha.strip().split(',')
            municipios.append({"nome": nome.strip(), "codigo": codigo.strip()})
    return municipios

# === Seleciona os indicadores com base no tipo de código IBGE ===
def selecionar_indicadores_por_local(codigo_local):
    """
    - 7 dígitos: município (n6)
    - 2 dígitos: estado (n3)
    """
    if len(codigo_local) == 7:
        return indicadores_municipios
    elif len(codigo_local) == 2:
        return indicadores_estados
    else:
        raise ValueError(f"Código inválido: {codigo_local}")

# === Coleta dados de qualquer local (município ou estado) ===
def coletar_dados_local(codigo_local):
    indicadores = selecionar_indicadores_por_local(codigo_local)
    dfs = []

    for nome_indicador, info in indicadores.items():
        tabela = info["tabela"]
        url = f"https://apisidra.ibge.gov.br/values/t/{tabela}/n6/{codigo_local}/p/last" if len(codigo_local) == 7 \
            else f"https://apisidra.ibge.gov.br/values/t/{tabela}/n3/{codigo_local}/p/last"

        headers = {"User-Agent": "Mozilla/5.0"}
        # print(f"Buscando {nome_indicador} (tabela {tabela}) para {codigo_local}...")

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
            df['indicador'] = nome_indicador
            dfs.append(df)
        except Exception as e:
            print(f"[Erro JSON] Indicador {nome_indicador}: {e}")
            print("Resposta:", response.text[:200])

    if dfs:
        return pd.concat(dfs, ignore_index=True)
    else:
        print("Nenhum dado coletado.")
        return pd.DataFrame()


# === Exemplo de uso ===
if __name__ == "__main__":
    path_municipios = os.path.join(os.path.dirname(__file__), 'municipios', 'municipios_filtrados.txt')
    municipios = carregar_municipios(path_municipios)

    if not municipios:
        print("⚠️ Nenhum município foi carregado. Verifique o arquivo.")
    else:
        municipio = municipios[0]  # Primeiro da lista
        cod_municipio = municipio["codigo"]
        cod_estado = cod_municipio[:2]  # primeiros 2 dígitos

        # Coleta dados do município
        df_mun = coletar_dados_local(cod_municipio)
        print(f"\n📊 Indicadores do Município: {municipio['nome']} ({cod_municipio})")
        if not df_mun.empty:
            for ind in df_mun["indicador"].unique():
                print(f"\n🔹 {ind}")
                print(df_mun[df_mun["indicador"] == ind][["Valor", "Ano"]].head(5))

        # Coleta dados do estado
        df_estado = coletar_dados_local(cod_estado)
        print(f"\n📊 Indicadores do Estado: código {cod_estado}")
        if not df_estado.empty:
            for ind in df_estado["indicador"].unique():
                print(f"\n🔹 {ind}")
                print(df_estado[df_estado["indicador"] == ind][["Valor", "Ano"]].head(5))


