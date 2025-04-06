from langchain.memory import ConversationSummaryBufferMemory
from langchain.agents import initialize_agent, AgentType
from langchain_groq import ChatGroq
from langchain.tools import Tool
import os
from dotenv import load_dotenv
from tools.sidra_tool import consultar_sidra
from tools.scraping_tool import buscar_info_web

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(temperature=0, model_name="llama3-8b-8192", api_key=groq_api_key)
memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=500)

tools = [
    Tool(
        name="consultar_sidra",
        func=consultar_sidra,
        description="Consulta dados do IBGE no SIDRA."
    ),
    Tool(
        name="Busca Web",
        func=buscar_info_web,
        description="Busca dados diretamente no site do IBGE."
    )
]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    memory=memory,
    handle_parsing_errors=True,
    verbose=True
)