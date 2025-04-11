import os
from dotenv import load_dotenv, find_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter

from langchain_cohere import CohereEmbeddings
from langchain_pinecone import PineconeVectorStore

from langchain.memory import ConversationBufferMemory

from langchain_groq import ChatGroq

from langchain import hub
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain

load_dotenv(find_dotenv())

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

loader = PyPDFLoader("C:\\Users\\Maria Raquel\\add-houer-pdf\\data\\INSTITUCIONAL HOUER_2024 (OUT).pdf")
documents = loader.load()

text_splitter = CharacterTextSplitter(separator="\n")
docs = text_splitter.split_documents(documents)

embeddings = CohereEmbeddings(model="embed-english-v3.0", cohere_api_key=COHERE_API_KEY)
index_name = "rag-demo"

vectorstore_from_docs = PineconeVectorStore.from_documents(
    docs, 
    index_name=index_name, 
    embedding=embeddings
)

vectorstore = PineconeVectorStore(index_name=index_name, embedding=embeddings)
print(vectorstore.similarity_search("fale sobre 1 projeto da houer"))

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

llm = ChatGroq(
    model="Gemma2-9b-It",
    groq_api_key=GROQ_API_KEY,
    temperature=0.1
)

retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
combine_docs_chain = create_stuff_documents_chain(
    llm, 
    retrieval_qa_chat_prompt
    )

retrieval_chain = create_retrieval_chain(
    vectorstore.as_retriever(), 
    combine_docs_chain
)

response = retrieval_chain.invoke({"input": "o que é a houer?"})
print(response['answer'])