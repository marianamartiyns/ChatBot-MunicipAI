import requests
import pandas as pd

## Existe busca na API de municipios por UF, poderia ser feito um filtro para buscar apenas os municipios de SP
## Existe busca na API de CNAE por grupo, poderia ser feito um filtro para buscar apenas os grupos de interesse, baseado no prompt de entrada do usuário no chatbot


def fetch_municipios():

    """
    Obtém a lista de municípios do Brasil utilizando a API de Localidades do IBGE.
    """

    url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        return df
    else:
        raise Exception(f"Erro ao acessar API de municípios: {response.status_code}")

def fetch_cnae_classes():

    """
    Obtém a lista de classes da CNAE utilizando a API do IBGE.
    """

    url = "https://servicodados.ibge.gov.br/api/v2/cnae/classes"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        return df
    else:
        raise Exception(f"Erro ao acessar API de CNAE: {response.status_code}")

if __name__ == "__main__":
    
    # Testando as funções
    df_municipios = fetch_municipios()
    print(df_municipios.head())

    df_cnae_classes = fetch_cnae_classes()
    print(df_cnae_classes.head())

    # print(df_cnae_classes.columns) # Colunas(['id', 'descricao', 'grupo', 'observacoes'], dtype='object')
    # print(df_municipios.columns) # Colunas(['id', 'nome', 'microrregiao', 'regiao-imediata'], dtype='object')

    # print(df_municipios['regiao-imediata'].unique()) # RESULTADO: ['Região Imediata de São Paulo' 'Região Imediata de Campinas' 'Região Imediata de Jundiaí' 'Região Imediata de Sorocaba' 'Região Imediata de Bragança Paulista' 'Região Imediata de Limeira' 'Região Imediata de Piracicaba' 'Região Imediata de Itapetininga' 'Região Imediata de Registro' 'Região Imediata de Itapeva' 'Região Imediata de Itararé' 'Região Imediata de Avaré' 'Região Imediata de Botucatu' 'Região Imediata de Ourinhos' 'Região Imediata de Assis' 'Região Imediata de Marília' 'Região Imediata de Tupã' 'Região Imediata de Lins' 'Região Imediata de Birigui' 'Região Imediata de Araçatuba' 'Região Imediata de Andradina' 'Região Imediata de Presidente Prudente' 'Região Imediata de Dracena' 'Região Imediata de Adamantina' '