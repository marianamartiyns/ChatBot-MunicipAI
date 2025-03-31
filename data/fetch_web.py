import requests
from bs4 import BeautifulSoup # pip install bs4
import pandas as pd

''' Código para realizar o WebScraping de informações dos estados brasileiros (https://youtu.be/OpX5Y7dzNjI?si=4vxgPNx31D-DnBWf)'''

# Função para realizar o WebScraping
def scrap_state_info(state: str) -> dict:
    """
    Retorna informações do estado brasileiro

    :param state: nome do estado
    :returns state_dict: dicionário com indicadores do estado
    """
    print(f'⛷️ Coletando informações de {state}...')
    state_url = f'https://www.ibge.gov.br/cidades-e-estados/{state}.html'
    
    try:
        page = requests.get(state_url, verify=False, timeout=10)
        page.raise_for_status()
    except requests.RequestException as e:
        print(f'Erro ao acessar {state_url}: {e}')
        return {'Estado': state}
    
    soup = BeautifulSoup(page.content, 'html.parser')
    indicadors = soup.select('.indicador')
    
    state_dict = {
        ind.select_one('.ind-label').text.strip(): ind.select_one('.ind-value').text.strip()
        for ind in indicadors if ind.select_one('.ind-label') and ind.select_one('.ind-value')
    }
    
    state_dict['Estado'] = state
    return state_dict

# Lista de estados brasileiros
states = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']

# Coleta dos dados
states_data = [scrap_state_info(state) for state in states]
df = pd.DataFrame(states_data)

# -------------------- Cleaning
states_df = df.copy()

# Ajuste de colunas (verificando inconsistências)
if states_df.shape[1] == 14:
    states_df.columns = [
        'governador', 'capital', 'gentilico', 'area', 'populacao', 'densidade_demografica', 
        'matriculas_ensino_fundamental', 'idh', 'receita_realizada', 'despesas_comprometidas', 
        'renda_per_capita', 'total_veiculos', 'codigo', 'coluna_extra'
    ]
    states_df.drop(columns=['coluna_extra'], inplace=True)

elif states_df.shape[1] == 13:
    states_df.columns = [
        'governador', 'capital', 'gentilico', 'area', 'populacao', 'densidade_demografica', 
        'matriculas_ensino_fundamental', 'idh', 'receita_realizada', 'despesas_comprometidas', 
        'renda_per_capita', 'total_veiculos', 'codigo'
    ]


# Limpeza de dados (remoção de caracteres indesejados)
states_df = states_df.replace({
    r'\.': '',
    r',': '.',
    r'\[\d+\]': '',
    r' hab/km²': '',
    r' km²': '',
    r' pessoas': '',
    r' matrículas': '',
    r'R\$.*': '',
    r' veículos': ''
}, regex=True)

# Conversão de colunas numéricas
num_cols = ['populacao', 'area', 'idh', 'renda_per_capita', 'total_veiculos', 'matriculas_ensino_fundamental', 'despesas_comprometidas', 'receita_realizada']
states_df[num_cols] = states_df[num_cols].apply(lambda x: x.str.strip() if x.dtype == "object" else x)

print(states_df.head())
print(states_df.columns)