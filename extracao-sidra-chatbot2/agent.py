from langchain.memory import ConversationSummaryBufferMemory
from langchain.agents import initialize_agent, AgentType
from langchain_groq import ChatGroq
from langchain.tools import Tool
import os
from dotenv import load_dotenv
from tools.sidra_tool import consultar_sidra_chatbot
from tools.scraping_tool import buscar_info_web
from langchain.schema import SystemMessage

from tools.sidra_tool import (
    consultar_sidra_chatbot,
    responder_coleta_sidra,
    responder_dados_estado
)


load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# === Carrega a mensagem de sistema personalizada ===
caminho_prompt = os.path.join(os.path.dirname(__file__), "prompts", "system_message.txt")
with open(caminho_prompt, "r", encoding="utf-8") as f:
    system_prompt = f.read()

llm = ChatGroq(
    temperature=0,
    model_name="llama3-8b-8192",
    api_key=groq_api_key,
)

memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=500)

tools = [
    Tool(
    name="Consulta Inteligente ao SIDRA",
    func=consultar_sidra_chatbot,
    description="Consulta dados do SIDRA com base em perguntas como 'PIB de Uberlândia', 'população de Contagem', etc. Deve ser usada primeiro para perguntas específicas."
    ),
    Tool(
    name="Coleta SIDRA Avançada",
    func=responder_coleta_sidra,
    description="Consulta múltiplos indicadores SIDRA para uma localidade (ex: saúde, educação, população)."
    ),
    Tool(
        name="Dados Estaduais Detalhados",
        func=responder_dados_estado,
        description="Dados públicos gerais sobre estados."
    ),
    Tool(
        name="Busca Web",
        func=buscar_info_web,
        description="Busca no site do IBGE caso os dados locais não estejam disponíveis."
    )

]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    memory=memory,
    handle_parsing_errors=True,
    verbose=True,
    system_message=SystemMessage(content=system_prompt) 
)