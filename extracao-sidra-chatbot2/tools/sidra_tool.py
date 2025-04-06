import pandas as pd
from sidrapy import get_table

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