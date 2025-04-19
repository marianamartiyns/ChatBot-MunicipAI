# backend\agent\app\main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.agent.agent import responder_pergunta , responder_houer
from backend.tools.fetch_wikipedia import coletar_dados_wikipedia

app = FastAPI()

# ==================== FERRAMENTAS PARA AGENTE ====================
# Permitir requisições do frontend (Next.js)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # substitua por ["http://localhost:3000"] se quiser restringir
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo da pergunta
class Pergunta(BaseModel):
    texto: str

# Rota de teste
@app.get("/")
def raiz():
    return {"mensagem": "✅ API do Chatbot Municípios está no ar."}

# Rota para receber perguntas do frontend

@app.post("/responder")
def responder(pergunta: Pergunta):
    return {"resposta": responder_pergunta(pergunta.texto)}

@app.post("/dados-houer")
def dados_houer(pergunta: Pergunta):
    return {"resposta": responder_houer(pergunta.texto)}


@app.get("/mensagem-inicial")
def mensagem_inicial():
    from backend.agent.agent import mensagem_inicial
    return {"mensagem": mensagem_inicial}

# ==================== FERRAMENTAS PARA O PAINEL ====================
from backend.tools.fetch_ibge import extrair_dados_municipio, carregar_dados_estaduais
from backend.tools.fetch_ibge import ESTADOS, MUNICIPIOS


class Codigo(BaseModel):
    codigo: str

@app.post("/dados-municipio")
def dados_municipio(codigo: Codigo):
    return extrair_dados_municipio(codigo.codigo)

@app.post("/dados-estado")
def dados_estado(codigo: Codigo):
    return carregar_dados_estaduais(codigo.codigo)

@app.get("/lista-estados")
def lista_estados():
    return [{"codigo": cod, **dados} for cod, dados in ESTADOS.items()]

@app.get("/lista-municipios")
def lista_municipios():
    return [{"codigo": cod, **dados} for cod, dados in MUNICIPIOS.items()]


# ==================== FERRAMENTAS WIKIPEDIA ====================

class Nome(BaseModel):
    nome: str

@app.post("/wikipedia-municipio")
def wikipedia_municipio(body: Nome):
    try:
        return coletar_dados_wikipedia(body.nome, tipo="municipio")
    except Exception as e:
        return {"erro": str(e)}

@app.post("/wikipedia-estado")
def wikipedia_estado(body: Nome):
    try:
        return coletar_dados_wikipedia(body.nome, tipo="estado")
    except Exception as e:
        return {"erro": str(e)}
    

