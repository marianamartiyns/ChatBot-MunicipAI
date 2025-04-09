import pandas as pd
from sidrapy import get_table
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from data.fetch_sidra import coletar_dados_local
from data.fetch_ibge_estados import carregar_dados_estaduais


def consultar_sidra(tabela, nivel_territorial, localidade, variaveis=None):
    """
    Consulta dados no SIDRA do IBGE com base na tabela, nível territorial e localidade.
    
    Args:
        tabela (str): Código da tabela do SIDRA.
        nivel_territorial (str): 'municipal' ou 'estadual'.
        localidade (str): Código IBGE do município ou estado.
        variaveis (str, opcional): Códigos das variáveis separadas por vírgula. Se não informado, consulta todas.

    Returns:
        pd.DataFrame ou str: DataFrame com os dados consultados ou mensagem de erro.
    """
    if nivel_territorial.lower() == 'municipal':
        nivel_cod = 6
    elif nivel_territorial.lower() == 'estadual':
        nivel_cod =  3
    else:
        return "Nível territorial inválido. Use 'municipal' ou 'estadual'."

    variaveis = variaveis.split(',') if variaveis else ['all']

    try:
        df = get_table(
            table_code=tabela,
            territorial_level=nivel_cod,
            ibge_territorial_code=[localidade],
            variable=variaveis,
            classificatory_code='all',
            classificatory_code_value='all',
            period='last'
        )

        if df.empty:
            return "Nenhum dado encontrado para esta consulta."
        
        return df.dropna().reset_index(drop=True)
    
    except Exception as e:
        return f"Erro ao consultar o SIDRA: {str(e)}"

def listar_campos_da_tabela(tabela):
    """
    Retorna os campos disponíveis em uma tabela do SIDRA.
    
    Args:
        tabela (str): Código da tabela do SIDRA.

    Returns:
        list: Lista de variáveis disponíveis na tabela.
    """
    exemplos = {
        '2938': ['PIB total', 'PIB per capita', 'Valor adicionado', 'Impostos líquidos'],
        '1419': ['Produção de leite', 'Rebanho ordenhado', 'Produtividade'],
        '6579': ['População residente total', 'População urbana', 'População rural']
    }
    return exemplos.get(str(tabela), ['Variáveis não identificadas para esta tabela.'])

def get_municipios_mg():
    """
    Retorna um dicionário com os códigos IBGE dos municípios de Minas Gerais.

    Returns:
        dict: Dicionário onde a chave é o nome do município e o valor é o código IBGE.
    """
    return {
        'Belo Horizonte': '3106200',
        'Uberlândia': '3170206',
        'Contagem': '3118601',
        'Juiz de Fora': '3136702',
    }

def get_cod_estado(nome_estado):
    """
    Retorna o código IBGE correspondente a um estado brasileiro.
    
    Args:
        nome_estado (str): Nome do estado.

    Returns:
        str: Código IBGE do estado ou o próprio nome se não encontrado.
    """
    estados = {
        'Minas Gerais': '31',
        'Paraíba': '25',
        'Paraná': '41',
        'Pernambuco': '26',
        'Piauí': '22',
        'Rio de Janeiro': '33',
        'Rio Grande do Norte': '24',
        'Rio Grande do Sul': '43',
    }
    return estados.get(nome_estado.strip().title(), nome_estado)


# ================= ADCIONAL (MARIANA) ====================
def consultar_sidra_chatbot(pergunta: str) -> str:
    from tools.sidra_tool import consultar_sidra, get_municipios_mg, get_cod_estado

    municipios = get_municipios_mg()
    pergunta_lower = pergunta.lower()

    municipio_encontrado = next((m for m in municipios if m.lower() in pergunta_lower), None)
    if municipio_encontrado:
        localidade = municipios[municipio_encontrado]
        nivel = "municipal"
    else:
        estado_encontrado = next((e for e in ["Minas Gerais", "Paraná", "Pernambuco", "Paraíba", "Rio de Janeiro"] if e.lower() in pergunta_lower), None)
        if estado_encontrado:
            localidade = get_cod_estado(estado_encontrado)
            nivel = "estadual"
        else:
            return (
                "Não encontrei dados diretamente no SIDRA sobre esse indicador para esse município.\n"
                "Você pode buscar manualmente no site do IBGE: https://www.ibge.gov.br\n\n"
                "Ou tente reformular a pergunta com outro termo mais comum, como 'PIB', 'população', etc."
            )

    if "pib" in pergunta_lower:
        tabela = "2938"
        variaveis = "37"
    elif "população" in pergunta_lower:
        tabela = "6579"
        variaveis = "93"
    elif "leite" in pergunta_lower:
        tabela = "1419"
        variaveis = "214"
    else:
        return (
            "🤔 Indicador não reconhecido. Tente usar termos como 'PIB', 'população' ou 'produção de leite'.\n"
            "Ou acesse o IBGE manualmente: https://www.ibge.gov.br"
        )

    resultado = consultar_sidra(tabela, nivel, localidade, variaveis)
    if isinstance(resultado, str):
        return f"⚠️ {resultado}\n\n🔗 Tente buscar diretamente em: https://www.ibge.gov.br"

    if resultado.empty:
        return "Nenhum dado foi retornado para essa consulta."

    try:
        linha = resultado.sort_values(by="Ano", ascending=False).iloc[0]
        valor = linha["Valor"]
        ano = linha["Ano"]
        unidade = linha.get("Unidade de Medida", "")
        valor_formatado = f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        return (
            f"📊 O valor solicitado é **{valor_formatado}** referente ao ano de **{ano}**.\n"
            f"🧾 Unidade de medida: {unidade if unidade else 'Não especificada'}"
        )
    except Exception as e:
        return f"✅ Dados foram encontrados, mas houve erro ao interpretar o resultado: {e}"

def responder_coleta_sidra(pergunta: str) -> str:
    municipios = get_municipios_mg()
    pergunta_lower = pergunta.lower()

    municipio = next((m for m in municipios if m.lower() in pergunta_lower), None)
    if municipio:
        cod = municipios[municipio]
    else:
        estado = next((e for e in ["Minas Gerais", "Paraná", "Pernambuco", "Paraíba", "Rio de Janeiro"] if e.lower() in pergunta_lower), None)
        cod = get_cod_estado(estado) if estado else None

    if not cod:
        return "Não consegui identificar a localidade. Tente incluir o nome correto do município ou estado."

    df = coletar_dados_local(cod)
    if isinstance(df, str) or df.empty:
        return "Nenhum dado encontrado na coleta automática do SIDRA."

    resumo = []
    for ind in df["indicador"].unique():
        try:
            linha = df[df["indicador"] == ind].sort_values(by="Ano", ascending=False).iloc[0]
            resumo.append(f"- **{ind}**: {linha['Valor']} ({linha['Ano']})")
        except:
            continue
    return "\n".join(resumo) if resumo else "Dados coletados, mas não foi possível resumir os indicadores."


def responder_dados_estado(pergunta: str) -> str:
    estados = ["Minas Gerais", "Paraná", "Pernambuco", "Paraíba", "Rio de Janeiro"]
    pergunta_lower = pergunta.lower()

    estado = next((e for e in estados if e.lower() in pergunta_lower), None)
    if not estado:
        return "Não consegui identificar o estado. Tente escrever o nome completo."

    cod = get_cod_estado(estado)
    dados = carregar_dados_estaduais(cod)
    if not dados:
        return "Não encontrei dados estaduais detalhados."

    return "\n".join([f"- **{k}**: {v}" for k, v in dados.items() if v])