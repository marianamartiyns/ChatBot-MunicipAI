import os
import mysql.connector  # Conectar e interagir com bancos de dados MySQL
import ollama  # Usar a API do Ollama para gerar respostas
from dotenv import load_dotenv  # Carregar variáveis de ambiente de um arquivo .env
from flask import Flask, render_template, request, jsonify  # Importa render_template para renderizar HTML

# Carregar variáveis do arquivo .env
load_dotenv()  # Carrega as variáveis de ambiente de um arquivo .env. Essas variáveis são configuradas fora do código, em um arquivo separado.

app = Flask(__name__)  # Inicializa o Flask, criando a aplicação web.

# Funções para interagir com o banco de dados
def connect_to_db(host, user, password, db_name):
    try:
        db_conn = mysql.connector.connect(  # Tenta se conectar ao BD
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        return db_conn  # Retorna a conexão se a conexão for bem-sucedida
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao banco de dados: {err}")  # Exibe erro se não conseguir conectar
        return None

def get_schema(cursor):
    cursor.execute("SHOW TABLES")  # Solicita todas as tabelas
    tables = cursor.fetchall()  # Obtém todas as tabelas
    schema = {}  # Dicionário para armazenar os nomes das tabelas e suas colunas
    for table in tables:
        table_name = table[0]
        cursor.execute(f"DESCRIBE {table_name}")  # Solicita as colunas de cada tabela
        columns = cursor.fetchall()  # Obtém as colunas da tabela
        schema[table_name] = [col[0] for col in columns]  # Armazena as colunas no dicionário
    return schema  # Retorna o esquema do banco de dados

def generate_sql_query(prompt):
    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])  # Envia o prompt para o modelo Ollama
    return response["message"]["content"]  # Retorna a consulta SQL gerada

def run_query(cursor, query):
    cursor.execute(query)  # Executa a consulta SQL
    result = cursor.fetchall()  # Obtém o resultado da consulta
    return result  # Retorna os dados obtidos

def generate_natural_language_response(question, query, result):
    response = ollama.chat(  # Envia dados para o modelo da Ollama gerar uma resposta em linguagem natural
        model="mistral",
        messages=[
            {
                "role": "user",
                "content": f"Question: {question}\nSQL Query: {query}\nSQL Response: {result}\nGenerate a natural language answer."
            }
        ]
    )
    return response["message"]["content"]  # Retorna a resposta gerada em linguagem natural

def main(question, db_config):
    db_conn = connect_to_db(db_config["host"], db_config["user"], db_config["password"], db_config["database"])  # Conecta ao banco
    if db_conn is None:  # Se não conseguir conectar, retorna um erro
        return "Erro ao conectar ao banco de dados."

    cursor = db_conn.cursor()  # Cria um cursor para interagir com o banco de dados
    schema = get_schema(cursor)  # Obtém o esquema do banco de dados

    # Criar o prompt para o modelo de IA com base no esquema e na pergunta do usuário
    schema_str = "\n".join([f"{table}: {', '.join(columns)}" for table, columns in schema.items()])  # Monta uma string com as tabelas e colunas
    prompt = f"""
    Based on the table schema below, write a SQL query that would answer the user's question:
    {schema_str}

    Question: {question}
    SQL Query:
    """

    # Gerar a consulta SQL
    sql_query = generate_sql_query(prompt)  # Gera a consulta SQL com o Ollama
    print("Generated SQL Query:", sql_query)

    # Executar a consulta SQL no banco de dados
    result = run_query(cursor, sql_query)  # Executa a consulta SQL no banco de dados

    # Gerar a resposta natural com base no resultado da consulta
    natural_language_response = generate_natural_language_response(question, sql_query, result)
    print("Natural Language Response:", natural_language_response)

    # Fechar a conexão com o banco de dados
    cursor.close()
    db_conn.close()

    return natural_language_response  # Retorna a resposta gerada

@app.route('/')
def index():
    """
    Rota que exibe o formulário HTML para o usuário interagir com o chatbot.
    """
    return render_template('index.html')  # Renderiza o arquivo HTML

@app.route('/chat', methods=['POST'])
def chat():
    """
    Rota que recebe a pergunta do usuário, executa a consulta SQL
    e retorna a resposta em linguagem natural.
    """
    data = request.get_json()  # Recebe os dados enviados pelo frontend
    question = data.get('question')  # Pergunta enviada pelo frontend
    db_config = data.get('db_config')  # Configuração do banco de dados

    if not question or not db_config:
        return jsonify({"error": "Missing question or database configuration"}), 400

    # Chama a função principal para processar a pergunta e gerar a resposta
    response = main(question, db_config)
    return jsonify({"response": response})  # Retorna a resposta em JSON

if __name__ == "__main__":
    app.run(debug=True)  # Inicia o servidor Flask
