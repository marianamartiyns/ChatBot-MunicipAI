# backend\agent\agent.py

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
    temperature=0.5,
    model_name="llama3-8b-8192",
    api_key=GROQ_API_KEY
)

# === Memória de conversa com recuperação de última localidade ===
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
ultima_localidade = {"tipo": "", "cod": "", "nome": ""}

# === Ferramentas de busca ===
from backend.tools.fetch_ibge import extrair_dados_municipio, carregar_dados_estaduais
from backend.tools.fetch_wikipedia import coletar_dados_wikipedia
from backend.data.fetch_houer import consultar_houer

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

    quer_estado = "estado" in palavras or "estado de" in pergunta_norm
    quer_municipio = "municipio" in palavras or "cidade" in palavras or "municipio de" in pergunta_norm

    if quer_estado:
        for cod, est in ESTADOS.items():
            nome = est.get("nome", "")
            sigla = est.get("sigla", "")
            nome_norm = normalizar_texto(nome)
            sigla_norm = normalizar_texto(sigla)
            if nome_norm in palavras or sigla_norm in palavras or nome_norm in pergunta_norm:
                return "estado", cod, nome

    if quer_municipio:
        for cod, mun in MUNICIPIOS.items():
            nome = mun.get("nome", "")
            nome_norm = normalizar_texto(nome)
            if nome_norm in palavras or nome_norm in pergunta_norm:
                return "municipio", cod, nome

    municipios_ordenados = sorted(MUNICIPIOS.items(), key=lambda x: -len(x[1].get("nome", "")))
    for cod, mun in municipios_ordenados:
        nome = mun.get("nome", "")
        nome_norm = normalizar_texto(nome)
        if nome_norm in pergunta_norm:
            return "municipio", cod, nome

    for cod, est in ESTADOS.items():
        nome = est.get("nome", "")
        sigla = est.get("sigla", "")
        nome_norm = normalizar_texto(nome)
        sigla_norm = normalizar_texto(sigla)
        if nome_norm in pergunta_norm or sigla_norm in pergunta_norm:
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

# === Função principal do agente (municipal/estadual) ===
def responder_pergunta(pergunta: str) -> str:
    global ultima_localidade
    try:
        # Detecta perguntas institucionais da Houer
        if any(p in pergunta.lower() for p in [
            "houer", "empresa", "serviços", "servicos", "missão", "visão", "proposito",
            "valores", "certificação", "concessões", "engenharia", "tecnologia",
            "áreas de atuação", "parceiros", "escritórios", "contato", "cultura", "compliance"
        ]):
            return responder_houer(pergunta)

        tipo, cod, nome = identificar_local(pergunta)

        if not tipo and ultima_localidade["cod"]:
            tipo, cod, nome = ultima_localidade["tipo"], ultima_localidade["cod"], ultima_localidade["nome"]

        if tipo and cod:
            ultima_localidade = {"tipo": tipo, "cod": cod, "nome": nome}
            dados_texto, fonte = coletar_dados_local(tipo, cod, nome)
        elif tipo and nome:
            dados = coletar_dados_wikipedia(nome, tipo=tipo)
            fonte = "Wikipedia"
            dados_texto = "\n".join([f"- {k}: {v}" for k, v in dados.items() if k.lower() != "fonte"])
            ultima_localidade = {"tipo": tipo, "cod": "", "nome": nome}
        else:
            return (
                "🤔 Não consegui identificar com clareza o município ou estado mencionados. "
                "Tente reformular sua pergunta ou incluir o nome completo do local."
            )

        prompt = f"""
Você é um assistente de dados públicos da Houer que responde de forma **clara, direta e objetiva**.
Use os dados abaixo para responder à pergunta do usuário. 
Se a informação exata não estiver disponível, informe isso com transparência e proponha o dado mais recente relacionado, se possível.
Evite repetir frases genéricas e não prolongue a resposta desnecessariamente.

Local consultado: {nome}
Fonte: {fonte}
Dados disponíveis:
{dados_texto}

Pergunta: {pergunta}

Resposta:"""
        resposta = llm.predict(prompt)
        return f"{resposta}\n\nFonte: {fonte}"

    except Exception as e:
        return (
            "Tivemos um problema ao processar sua pergunta. "
            "Por favor, tente novamente em instantes."
        )


# === Função específica para perguntas sobre a Houer ===
def responder_houer(pergunta: str) -> str:
    try:
        resposta = consultar_houer(pergunta)
        if "❌" in resposta:
            return (
                "Informação não encontrada nos dados institucionais da Houer. "
                "Verifique se a pergunta está correta ou reformule."
            )
        return f"{resposta}\n\nFonte: dados institucionais Houer"
    except Exception as e:
        return "Ocorreu um erro ao consultar dados institucionais da Houer."

# === Mensagem inicial automática ===
mensagem_inicial = (
    "Olá! 👋 Seja bem-vindo(a) ao assistente de dados municipais e estaduais do Brasil da Houer. "
    "Estou aqui para te ajudar com dados reais e explicações claras. É só mandar sua pergunta! 😊"
)
