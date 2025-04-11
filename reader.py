import os
import streamlit as st
from dotenv import load_dotenv, find_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter

from langchain_cohere import CohereEmbeddings
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore

from langchain.memory import ConversationBufferMemory
from langchain_groq import ChatGroq
from langchain import hub
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain

# Carrega variáveis de ambiente
load_dotenv(find_dotenv())

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Título do app
st.set_page_config(page_title="Informações sobre a Houer", layout="wide")
st.title("📚 Consulta de informações sobre a Houer")

@st.cache_resource
def setup():
    # 1. Carrega e divide o PDF
    loader = PyPDFLoader("C:\\Users\\Maria Raquel\\add-houer-pdf\\data\\INSTITUCIONAL HOUER_2024 (OUT).pdf")
    documents = loader.load()
    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(documents)

    # 2. Gera embeddings
    embeddings = CohereEmbeddings(model="embed-english-v3.0", cohere_api_key=COHERE_API_KEY)

    # 3. Inicializa Pinecone
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index_name = "rag-demo"

    # Cria o índice se não existir
    if index_name not in [i.name for i in pc.list_indexes()]:
        pc.create_index(
            name=index_name,
            dimension=1024,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )

    # 4. Envia documentos para o índice
    vectorstore = PineconeVectorStore.from_documents(
        documents=docs,
        embedding=embeddings,
        index_name=index_name,
        namespace="default"
    )

    # 5. Configura o modelo e corrente de recuperação
    llm = ChatGroq(
            model="llama3-8b-8192",  # ou "gemma-7b-it"
            groq_api_key=GROQ_API_KEY,
            temperature=0.1
            )

    prompt = hub.pull("langchain-ai/retrieval-qa-chat")
    combine_docs_chain = create_stuff_documents_chain(llm, prompt)
    retrieval_chain = create_retrieval_chain(vectorstore.as_retriever(), combine_docs_chain)

    return retrieval_chain

retrieval_chain = setup()

# Histórico de chat
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Campo de entrada do usuário
user_input = st.chat_input("Faça sua pergunta sobre o PDF...")

# Mostra histórico
for user_msg, bot_msg in st.session_state.chat_history:
    with st.chat_message("user"):
        st.markdown(user_msg)
    with st.chat_message("assistant"):
        st.markdown(bot_msg)

# Nova pergunta
if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Consultando..."):
        response = retrieval_chain.invoke({"input": user_input})
        answer = response['answer']

    with st.chat_message("assistant"):
        st.markdown(answer)

    # Atualiza histórico
    st.session_state.chat_history.append((user_input, answer))