from sidrapy import get_table
import pandas as pd

'''
Mapeando os temas do SIDRA para os códigos de tabela do IBGE.

1411 - População Residente: Dados sobre a população residente no Brasil, estados e municípios.
1943 - PIB dos Municípios e Estados: Produto Interno Bruto (PIB) dos estados e municípios brasileiros.
2919 - Índice de Preços ao Consumidor: Índices de preços para o cálculo da inflação.
2730 - Taxa de Mortalidade: Taxas de mortalidade geral, por faixa etária e causas específicas de morte.
4310 - Educação (Matrículas de Ensino Fundamental e Médio): Dados sobre matrículas no ensino fundamental e médio.
5931 - Emprego e Rendimento do Trabalho: Informações sobre emprego, taxas de desemprego e rendimentos do trabalho.
2450 - Infraestrutura e Saneamento: Dados sobre serviços de saneamento básico e infraestrutura.
2106 - Saúde (Equipamentos e Recursos): Dados sobre recursos de saúde disponíveis nos municípios.
5063 - Agricultura (Produção): Dados sobre a produção agrícola por município.
6552 - Transporte (Frota de Veículos): Dados sobre o transporte e frota de veículos nos municípios.

'''

# Dicionários com os códigos IBGE de estados e alguns municípios para exemplo
CODES_IBGE_ESTADOS = {
    "são paulo": "35", "rio de janeiro": "33", "bahia": "29", "minas gerais": "31",
    "sp": "35", "rj": "33", "ba": "29", "mg": "31"
}

municipios_ibge = {
    "são paulo": "3550308",
    "rio de janeiro": "3304557",
    "salvador": "2927408",
    "belo horizonte": "3106200"
}

def consultar_sidra(tabela, localidade=None, ano="2021"):
    """
    Consulta dados do SIDRA informando o código da tabela, a localidade (estado ou município)
    e o ano desejado. (Feito com o ChatGPT)

    Parâmetros:
    - tabela (str): Código da tabela do SIDRA.
    - localidade (str): Nome do estado ou município (opcional).
    - ano (str): Ano da consulta (padrão: 2021).

    Retorno:
    - DataFrame com os dados consultados.
    """
    try:
        territorial_level = "1"  # Nível Brasil por padrão
        ibge_code = "all"  # Código para trazer todos os dados disponíveis

        # Se uma localidade foi informada, verificamos se é estado ou município
        if localidade:
            localidade_lower = localidade.lower()
            if localidade_lower in CODES_IBGE_ESTADOS:
                ibge_code = CODES_IBGE_ESTADOS[localidade_lower]  # Código do estado
                territorial_level = "3"  # Estados
            elif localidade_lower in municipios_ibge:
                ibge_code = municipios_ibge[localidade_lower]  # Código do município
                territorial_level = "4"  # Municípios
            else:
                raise ValueError("Localidade não encontrada. Verifique o nome do estado ou município.")

        # Requisição para o SIDRA
        dados = get_table(
            table_code=str(tabela),
            territorial_level=str(territorial_level),
            period=ano,
            ibge_territorial_code=str(ibge_code)
        )

        # Converter para DataFrame e exibir os primeiros dados
        df = pd.DataFrame(dados)
        print(f"\n📊 Dados da Tabela {tabela} para {localidade or 'Brasil'} no ano {ano}:")
        print(df.head())

        return df
    except Exception as e:
        print(f"Erro ao consultar SIDRA: {e}")
        return None

# Exemplos de uso -  Percebi que o nome real das colunas está na linha (0), por isso estou redefinindo com iloc[0] (sugestão: colocar essa modificação dentro da função)

df1 = consultar_sidra("1411")  # População do Brasil - outros codigos estão dando erro, mas o 1411 está funcionando
df1.columns = df1.iloc[0]  # Define a primeira linha como cabeçalho
df1 = df1[1:] 
df1 = df1.reset_index(drop=True)  # Reseta os índices para organizar melhor

print(df1.head())
print(df1.columns)

# df_pib = consultar_sidra("1943")
# print(df_pib.head())
# print(df_pib.columns)

# tá dando erro: df2 = consultar_sidra("1411", "são paulo")  # População do Estado de São Paulo
# tá dando erro: df3 = consultar_sidra("1411", "salvador")  # População do Município de Salvador
