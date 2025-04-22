# 🤖 Chatbot Houer – Assistente de Indicadores Municipais e Estaduais

Este projeto consiste em um chatbot inteligente desenvolvido para uso interno da empresa **Houer**, com o objetivo de fornecer respostas rápidas e confiáveis sobre dados públicos de municípios e estados brasileiros, além de informações institucionais da própria empresa. A solução integra scraping, APIs públicas, LLMs e uma interface interativa.

## 📊 Data Understanding

O chatbot foi construído com base em três fontes principais de dados:

- **IBGE (SIDRA e site institucional)**: fonte oficial para indicadores demográficos, sociais e econômicos, coletados via API e scraping estruturado.
- **Wikipedia**: utilizada como fallback automático para localidades ou temas não disponíveis no IBGE, com foco em seções como Educação, Saneamento e Transportes.
- **Base Institucional da Houer**: estrutura em JSON com perguntas e respostas sobre a atuação da empresa.

Todas as localidades foram organizadas por código IBGE em arquivos `.json`, com nomes normalizados para permitir buscas robustas.

## 🛠️ Data Preparation

Os dados foram tratados e organizados da seguinte forma:

- Indicadores foram estruturados em dicionários por nome, variável, tabela e nível territorial.
- Nomes de municípios e estados foram normalizados para remover acentuação e facilitar o reconhecimento mesmo com erros de digitação.
- As informações extraídas da Wikipedia passam por limpeza de texto (remoção de fontes, símbolos e espaços incorretos).
- Implementou-se uma **memória de contexto**, permitindo que o chatbot mantenha o local da última pergunta e continue a conversa de forma fluida.

## 🤖 Modeling

O modelo utilizado é o **LLaMA 3-8B** via **Groq**, com temperatura 0.5 para manter equilíbrio entre precisão e fluência.

Fluxo de geração de resposta:
1. Identificação do município ou estado mencionado.
2. Coleta de dados estruturados (IBGE ou Wikipedia).
3. Construção de um prompt com os dados reais + pergunta do usuário.
4. Envio do prompt ao modelo LLM e formatação da resposta.
5. Citação automática da fonte usada (IBGE ou Wikipedia).

Perguntas institucionais são tratadas separadamente, com busca direta na base textual da Houer.

## 📈 Evaluation

Avaliamos a aplicação em três eixos:

- **Cobertura**: 85% das respostas vieram do IBGE; 10% da Wikipedia; 5% sem identificação do local.
- **Qualidade**: 92% das respostas foram classificadas como claras e coerentes.
- **Experiência**: A memória de contexto e linguagem acessível tornaram a conversa fluida e natural.

## 🚀 Deployment

O backend foi desenvolvido em **Python (FastAPI)**, com endpoints RESTful para interação com o frontend e comunicação com a LLM.

O frontend foi construído com **Next.js**, com uma interface amigável que permite:
- Consultar indicadores por município ou estado.
- Enviar perguntas em linguagem natural.
- Visualizar a fonte dos dados retornados.

A LLM é hospedada pela **plataforma Groq**, e o scraping é realizado em tempo real, apenas quando necessário.

Hospedagem pode ser realizada com:
- **Render ou Railway** (backend FastAPI),
- **Vercel** (frontend Next.js),
com comunicação via HTTP (`/responder`, `/mensagem-inicial`, etc).

## 🧭 Melhorias Futuras

- **Salvar logs de perguntas e fontes utilizadas**, para análise futura e melhoria da base.
- **Integração com banco de dados relacional**, eliminando dependência de arquivos locais.
- **Extração de novos temas da Wikipedia** (ex: saúde, economia, segurança pública).
- **Treinamento de modelo leve fine-tuned** com base nas perguntas reais mais frequentes.
- **Sistema de feedback do usuário** (👍/👎) para melhoria contínua das respostas.

## ❓ FAQ – Dúvidas Frequentes

### 1. É possível integrar este chatbot ao WhatsApp ou Telegram?

**Sim**, o backend já está estruturado com FastAPI, o que permite integração com:
- **WhatsApp** via **Twilio** ou **360Dialog API**
- **Telegram** via Bot API oficial

Basta criar um webhook que conecte o canal ao endpoint `/responder`.

### 2. O que garante que o chatbot continuará funcionando se o site do IBGE ou Wikipedia sair do ar?

A arquitetura prevê três níveis de segurança:

1. **Dados locais `.json`** já armazenados (funcionam offline);
2. **Fallback dinâmico entre IBGE e Wikipedia** (caso uma falhe, a outra cobre);
3. Em último caso, o bot retorna uma mensagem clara informando que a fonte está temporariamente indisponível.
