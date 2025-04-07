import requests
import pandas as pd

# ================= RASCUNHO ==========================
# ========= Não está integrado no projeto, falta ajeitar para colher mais informações especificas =============

# Primeiro, pega os estados com seus códigos
estados_url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
res = requests.get(estados_url)
estados = res.json()

municipios_lista = []

# Para cada estado, pega os municípios
for estado in estados:
    uf_nome = estado['nome']
    uf_sigla = estado['sigla']
    uf_id = estado['id']
    
    print(f'Pegando municípios de {uf_nome} ({uf_sigla})...')
    
    municipios_url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf_id}/municipios"
    res_mun = requests.get(municipios_url)
    municipios = res_mun.json()
    
    for municipio in municipios:
        municipios_lista.append({
            'estado': uf_nome,
            'uf': uf_sigla,
            'municipio': municipio['nome'],
            'id_municipio': municipio['id']
        })

# Transforma em DataFrame
df_municipios = pd.DataFrame(municipios_lista)

print(df_municipios.head())
print(f'\nTotal de municípios coletados: {len(df_municipios)}')
print(df_municipios.columns)
