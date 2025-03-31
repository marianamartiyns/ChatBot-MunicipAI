# 🤖 Chatbot de Consultas SQL

> Chatbot interativo que converte perguntas em linguagem natural em consultas SQL e retorna respostas de um banco de dados MySQL.

## 📋 Descrição

Este projeto é um chatbot desenvolvido utilizando Flask, que permite aos usuários fazerem perguntas sobre um banco de dados MySQL em linguagem natural. As perguntas são convertidas automaticamente em consultas SQL, executadas no banco de dados e as respostas são retornadas de forma clara e compreensível. O chatbot usa a API Ollama com o modelo "mistral" para gerar as consultas SQL e fornecer respostas em linguagem natural.

## 🛠 Tecnologias Utilizadas
- **Python** (Flask)
- **HTML, CSS e JavaScript**
- **MySQL** para o banco de dados
- **Ollama API** para gerar consultas SQL
- **dotenv** para gerenciamento de variáveis de ambiente

## 📂 Estrutura do Projeto
```
|-- templates/
|   |-- index.html  # Interface do chatbot
|-- data/
|   |-- fetch_sidra.py  # Scripts para coleta de dados
|   |-- fetch_api.py
|   |-- fetch_web.py
|-- .env            # Arquivo de configuração do banco de dados (Não deve ser compartilhado)
|-- .gitignore      # Ignora arquivos sensíveis (.env, venv)
|-- main.py         # Servidor Flask que processa as perguntas e interage com o banco de dados
|-- requirements.txt # Dependências do projeto
```

## ⚙️ Configuração do Ambiente
1. Clone este repositório:
   ```sh
   git clone https://github.com/renantorres0/Chatbot_BOT6_teste.git
   ```
2. Navegue até a pasta do projeto:
   ```sh
   cd Chatbot_BOT6_teste
   ```
3. Crie um ambiente virtual:
   ```sh
   python -m venv venv
   source venv/bin/activate  # Para Linux/Mac
   venv\Scripts\activate     # Para Windows
   ```
4. Instale as dependências:
   ```sh
   pip install -r requirements.txt
   ```

### 📜 Arquivo `requirements.txt`
O projeto requer as seguintes bibliotecas para funcionar corretamente:
```
annotated-types==0.7.0
anyio==4.8.0
blinker==1.9.0
certifi==2025.1.31
click==8.1.8
colorama==0.4.6
Flask==3.1.0
h11==0.14.0
httpcore==1.0.7
httpx==0.28.1
idna==3.10
itsdangerous==2.2.0
Jinja2==3.1.6
MarkupSafe==3.0.2
mysql-connector-python==9.2.0
ollama==0.4.7
pydantic==2.10.6
pydantic_core==2.27.2
python-dotenv==1.0.1
sniffio==1.3.1
typing_extensions==4.12.2
Werkzeug==3.1.3
```

## 🚀 Uso
1. Acesse a interface web no navegador: [http://127.0.0.1:5000](http://127.0.0.1:5000)
2. Digite uma pergunta relacionada ao banco de dados e envie.
3. O chatbot converterá a pergunta em uma consulta SQL, executará a consulta e retornará a resposta em linguagem natural.

## 🤝 Contribuição
Sinta-se à vontade para contribuir com o projeto! Você pode:
- Enviar um **Pull Request** para corrigir bugs ou adicionar novos recursos
- Reportar **problemas** ou **melhorias** na aba de **Issues**
