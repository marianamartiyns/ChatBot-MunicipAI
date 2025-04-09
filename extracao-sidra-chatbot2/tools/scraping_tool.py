import requests
from bs4 import BeautifulSoup

def buscar_info_web(termo):
    url = f"https://www.ibge.gov.br/busca.html?q={termo}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    resposta = requests.get(url, headers=headers)
    
    if resposta.status_code != 200:
        return "Erro ao acessar o site do IBGE."
    
    soup = BeautifulSoup(resposta.text, "html.parser")
    resultados = soup.find_all("a", class_="resultado-busca-link")
    
    if resultados:
        return f"Encontrei algo no IBGE: [{resultados[0].text}]({resultados[0]['href']})"
    else:
        return "Nenhuma informação relevante encontrada."
    