# Web Scraping com Python - IBGE
# https://servicodados.ibge.gov.br/api/docs

# ========= Já está integrado no projeto, pode editar para melhorar =============

import pandas as pd
import requests
from bs4 import BeautifulSoup

estados = [
    'ac', 'al', 'ap', 'am', 'ba', 'ce', 'df', 'es', 'go', 'ma',
    'mt', 'ms', 'mg', 'pa', 'pb', 'pr', 'pe', 'pi', 'rj', 'rn',
    'rs', 'ro', 'rr', 'sc', 'sp', 'se', 'to'
]

def extrair_indicadores_estado(uf: str) -> dict:
    estado_url = f'https://www.ibge.gov.br/cidades-e-estados/{uf}.html'
    page = requests.get(estado_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    indicadores = soup.select('.indicador')

    inf_do_estado = {}
    for ind in indicadores:
        label = ind.select_one('.ind-label')
        valor = ind.select_one('.ind-value')
        if label and valor:
            inf_do_estado[label.text.strip()] = valor.text.strip()

    inf_do_estado['UF'] = uf.upper()
    return inf_do_estado

def coletar_indicadores_estaduais() -> pd.DataFrame:
    dados = [extrair_indicadores_estado(uf) for uf in estados]
    return pd.DataFrame(dados)


'''
# Total de estados: 27

# Colunas disponíveis: ['Governador', 'Capital', 'Gentílico', 'Área Territorial', 'População no último censo', 'Densidade demográfica', 'População estimada', 'Matrículas no ensino fundamental', 'IDH ÍndiColunas disponíveis: ['Governador', 'Capital', 'Gentílico', 'Área Territorial', 'População no último censo', 'Densidade demográfica', 'População estimada', 'Matrículas no ensino fundamental', 'IDH Índidice de desenvolvimento humano', 'Total de receitas brutas realizadas', 'Total de despesas brutas empenhadas', 'Rendimento mensal domiciliar per capita', 'Total de veículos', 'UF'] '''


