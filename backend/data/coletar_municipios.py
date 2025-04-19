import os
import json
import requests
import unicodedata

# pra rodar: python backend\data\coletar_municipios.py

CAMINHO_MUNICIPIOS = os.path.join(os.path.dirname(__file__), "municipios.json")
CAMINHO_ESTADOS = os.path.join(os.path.dirname(__file__), "estados.json")

def normalizar(texto):
    return unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("ASCII").lower()

def coletar_municipios_e_estados():
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
    resposta = requests.get(url)

    if resposta.status_code != 200:
        raise Exception(f"Erro ao buscar municípios: {resposta.status_code}")

    dados = resposta.json()
    municipios = {}
    estados = {}

    for m in dados:
        cod_municipio = str(m["id"])
        nome_municipio = m["nome"]
        uf = m["microrregiao"]["mesorregiao"]["UF"]
        cod_estado = str(uf["id"])
        nome_estado = uf["nome"]

        municipios[cod_municipio] = {
            "nome": nome_municipio,
            "cod_estado": cod_estado,
            "nome_normalizado": normalizar(nome_municipio)
        }

        if cod_estado not in estados:
            estados[cod_estado] = {
                "nome": nome_estado,
                "sigla": uf["sigla"],
                "nome_normalizado": normalizar(nome_estado)
            }

    os.makedirs(os.path.dirname(CAMINHO_MUNICIPIOS), exist_ok=True)

    with open(CAMINHO_MUNICIPIOS, "w", encoding="utf-8") as f:
        json.dump(municipios, f, ensure_ascii=False, indent=2)

    with open(CAMINHO_ESTADOS, "w", encoding="utf-8") as f:
        json.dump(estados, f, ensure_ascii=False, indent=2)

    print(f"{len(municipios)} municípios salvos em {CAMINHO_MUNICIPIOS}")
    print(f"{len(estados)} estados salvos em {CAMINHO_ESTADOS}")

if __name__ == "__main__":
    coletar_municipios_e_estados()
