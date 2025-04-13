# backend/agent/agent.py

import json
import os
from dotenv import load_dotenv
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage
from langchain_groq import ChatGroq

# Imports das ferramentas reais
from backend.tools.fetch_sidra import responder_coleta_sidra
from backend.tools.fetch_ibge import (
    extrair_dados_municipio,
    carregar_dados_estaduais
)

# Carregamento de dados locais
with open("backend/data/municipios.json", encoding="utf-8") as f:
    MUNICIPIOS = json.load(f)

with open("backend/data/estados.json", encoding="utf-8") as f:
    ESTADOS = json.load(f)

# === Configuração do ambiente ===
load_dotenv()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# === Configuração da LLM via GROQ ===
llm = ChatGroq(
    temperature=0.3,
    model_name="llama3-8b-8192",
    api_key=GROQ_API_KEY
)

# === Memória do agente  ===
memory = ConversationBufferMemory(memory_key="chat_history")

# === Funções auxiliares ===
def _extrair_dados_municipio_via_pergunta(pergunta: str) -> str:
    pergunta_lower = pergunta.lower()
    for cod, mun in MUNICIPIOS.items():
        if mun["nome"].lower() in pergunta_lower:
            dados = extrair_dados_municipio(cod)
            return "\n".join([f"- **{k}**: {v}" for k, v in dados.items() if k != "Fonte"])
    return "Município não identificado. Por favor, informe um nome correto."

def _extrair_dados_estado_via_pergunta(pergunta: str) -> str:
    pergunta_lower = pergunta.lower()
    for cod, est in ESTADOS.items():
        if est["nome"].lower() in pergunta_lower:
            dados = carregar_dados_estaduais(cod)
            return "\n".join([f"- **{k}**: {v}" for k, v in dados.items() if k != "Fonte"])
    return "Estado não identificado. Por favor, informe um nome correto."

# === Ferramentas do agente ===
tools = [
    Tool(
        name="ConsultarIndicadoresSIDRA",
        func=responder_coleta_sidra,
        description="Use para obter dados como PIB, população ou indicadores do IBGE via SIDRA."
    ),
    Tool(
        name="ConsultarMunicipioScraping",
        func=_extrair_dados_municipio_via_pergunta,
        description="Use para consultar indicadores de um município usando a página do IBGE."
    ),
    Tool(
        name="ConsultarEstadoScraping",
        func=_extrair_dados_estado_via_pergunta,
        description="Use para consultar indicadores de um estado usando a página do IBGE."
    ),
]

# === System prompt (com personalidade e instrução de segurança) ===
with open("backend/agent/prompts/system_message.txt", encoding="utf-8") as f:
    system_message = SystemMessage(content=f.read())

# === Inicialização do agente ===
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    memory=memory,
    agent_kwargs={"system_message": system_message},
    verbose=True
)

# === Formatação da resposta === *
def formatar_resposta(resposta: str) -> str:
    if not resposta or "Exception" in resposta:
        return (
            "Tivemos um problema ao processar a sua pergunta. "
            "Tente novamente em alguns instantes.\n\n"
        )

    if "Município não identificado" in resposta or "Estado não identificado" in resposta:
        return (
            "Não conseguimos reconhecer o local informado. "
            "Tente reformular usando o nome completo e correto do município ou estado.\n\n"
            "Fontes consultadas: Lista de municípios e estados do IBGE."
        )

    if any(x in resposta.lower() for x in ["not found", "não disponível", "not valid", "not available"]):
        return (
            "A informação solicitada não está disponível nas fontes públicas consultadas no momento.\n\n"
        )

    # Supondo que o dado esteja certo, adiciona fonte padrão:
    if "Fonte" not in resposta:
        resposta += "\n\nFonte: IBGE (dados oficiais ou SIDRA)"
    return resposta



# === Função para uso externo ===
'''def responder_pergunta(pergunta: str) -> str:
    return agent.run(pergunta)'''
def responder_pergunta(pergunta: str) -> str:
    try:
        resposta_bruta = agent.run(pergunta)
        return formatar_resposta(resposta_bruta)
    except Exception as e:
        return "⚠️ Erro inesperado ao processar sua pergunta. Por favor, tente novamente."

