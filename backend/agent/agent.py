import json
import os
import unicodedata
import re
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage
from langchain_groq import ChatGroq

# === Carregamento dos dados locais ===
with open("backend/data/municipios.json", encoding="utf-8") as f:
    MUNICIPIOS = json.load(f)

with open("backend/data/estados.json", encoding="utf-8") as f:
    ESTADOS = json.load(f)

# === Configuração do ambiente ===
load_dotenv()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# === Configuração da LLM ===
llm = ChatGroq(
    temperature=0.2,
    model_name="llama3-8b-8192",
    api_key=GROQ_API_KEY
)

# === Memória de conversa (caso necessário futuramente) ===
memory = ConversationBufferMemory(memory_key="chat_history")

# === Ferramentas de busca ===
from backend.tools.fetch_ibge import extrair_dados_municipio, carregar_dados_estaduais
from backend.tools.fetch_wikipedia import coletar_dados_wikipedia

# === Função de normalização ===
def normalizar_texto(texto):
    if not texto:
        return ""
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ASCII", "ignore").decode("ASCII")
    texto = re.sub(r"[^\w\s]", "", texto)
    return texto.lower().strip()

# === Identificação da localidade ===
def identificar_local(pergunta: str):
    pergunta_norm = normalizar_texto(pergunta)
    palavras = set(pergunta_norm.split())

    for cod, mun in MUNICIPIOS.items():
        nome = mun.get("nome", "")
        nome_norm = normalizar_texto(nome)
        if len(nome_norm) <= 3:
            continue
        if nome_norm in pergunta_norm or nome_norm in palavras:
            return "municipio", cod, nome

    for cod, est in ESTADOS.items():
        nome = est.get("nome", "")
        sigla = est.get("sigla", "")
        nome_norm = normalizar_texto(nome)
        sigla_norm = normalizar_texto(sigla)
        if nome_norm in pergunta_norm or sigla_norm in palavras:
            return "estado", cod, nome

    return "", "", ""

# === Coleta e formatação dos dados ===
def coletar_dados_local(tipo: str, cod: str, nome: str) -> tuple[str, str]:
    if tipo == "municipio":
        dados = extrair_dados_municipio(cod)
        if not dados:
            dados = coletar_dados_wikipedia(nome, tipo="municipio")
            fonte = "Wikipedia"
        else:
            fonte = "IBGE"
    else:
        dados = carregar_dados_estaduais(cod)
        if not dados:
            dados = coletar_dados_wikipedia(nome, tipo="estado")
            fonte = "Wikipedia"
        else:
            fonte = "IBGE"

    texto_dados = "\n".join([f"- {k}: {v}" for k, v in dados.items() if k.lower() != "fonte"])
    return texto_dados, fonte

# === Função principal do agente ===
def responder_pergunta(pergunta: str) -> str:
    try:
        tipo, cod, nome = identificar_local(pergunta)

        if tipo:
            dados_texto, fonte = coletar_dados_local(tipo, cod, nome)

            prompt = f"""
Você é um assistente de dados públicos que responde de forma **clara, direta e objetiva**.
Use os dados abaixo para responder à pergunta do usuário. Se a informação exata não estiver nos dados, diga isso de forma curta e transparente — sem enrolar.

Local consultado: {nome}
Fonte: {fonte}
Dados disponíveis:
{dados_texto}

Pergunta: {pergunta}

Resposta:"""


            resposta = llm.predict(prompt)
            return f"{resposta}\n\n Fonte: {fonte}"

        else:
            # Pergunta sem local identificado — resposta genérica
            resposta = llm.predict(f"Responda de forma clara e confiável: {pergunta}")
            return resposta

    except Exception as e:
        return "⚠️ Ocorreu um erro inesperado ao processar sua pergunta. Tente novamente em instantes."

# === Mensagem inicial automática ===
mensagem_inicial = (
    "Olá! 👋 Seja bem-vindo(a) ao assistente de dados municipais e estaduais do Brasil da Houer. "
    "Estou aqui para te ajudar com dados reais e explicações claras. É só mandar sua pergunta! 😊"
)
