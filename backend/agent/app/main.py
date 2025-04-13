# backend\agent\app\main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.agent.agent import responder_pergunta  # importa do agent.py

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
    resposta = responder_pergunta(pergunta.texto)
    return {"resposta": resposta}

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



