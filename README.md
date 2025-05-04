# 🤖 Chatbot – Assistente de Indicadores Municipais e Estaduais

> Chatbot inteligente com Painel de Indicadores desenvolvido para uso interno de uma empresa privada, com o objetivo de fornecer respostas rápidas e confiáveis sobre dados públicos de municípios e estados brasileiros, além de informações institucionais da própria empresa. A solução integra scraping, APIs públicas, LLMs e uma interface interativa.

O chatbot foi construído com base em três fontes principais de dados:

- **IBGE (SIDRA e site institucional)**: fonte oficial para indicadores demográficos, sociais e econômicos, coletados via API e scraping estruturado.
- **Base Institucional da Empresa**: estrutura em JSON com perguntas e respostas sobre a atuação da empresa (dados disponibilizados via Website oficial).

Todas as localidades foram organizadas por código IBGE em arquivos `.json`, com nomes normalizados.

https://github.com/user-attachments/assets/6a15b904-fa2e-4f24-8063-8d694701d1b2

### 🔨 Modeling

O modelo utilizado é o **LLaMA 3-8B** via **Groq**, com temperatura 0.5 para manter equilíbrio entre precisão e fluência.

> Fluxo de geração de resposta:
> 1. Identificação do município ou estado mencionado.
> 2. Coleta de dados estruturados (SIDRA ou IBGE CIDADES).
> 3. Construção de um prompt com os dados reais + pergunta do usuário.
> 4. Envio do prompt ao modelo LLM e formatação da resposta.
> 5. Citação automática da fonte usada.

Perguntas institucionais são tratadas separadamente, com busca direta na base textual da empresa.

### 🚀 Deployment

O backend foi desenvolvido em **Python (FastAPI)**, com endpoints RESTful para interação com o frontend e comunicação com a LLM.

O frontend foi construído com **Next.js**, com uma interface que permite:
- Consultar indicadores por município ou estado.
- Enviar perguntas em linguagem natural.
- Visualizar a fonte dos dados retornados.

A LLM é hospedada pela **plataforma Groq**, e o scraping é realizado em tempo real, apenas quando necessário.

> [!note]
> Hospedagem pode ser realizada com:
> - **Render ou Railway** (backend FastAPI),
> - **Vercel** (frontend Next.js), com comunicação via HTTP (`/responder`, `/mensagem-inicial`, etc).

### 🧭 Melhorias Futuras

- [ ] **Salvar logs de perguntas e fontes utilizadas**, para análise futura e melhoria da base.
- [ ] **Integração com banco de dados relacional**, eliminando dependência de arquivos locais.
- [ ] **Extração de novos temas** (ex: saúde, economia, segurança pública).
- [ ] **Treinamento de modelo leve fine-tuned** com base nas perguntas reais mais frequentes.
- [ ] **Sistema de feedback do usuário** (👍/👎) para melhoria contínua das respostas.

```
❓ FAQ – Dúvidas Frequentes

1. É possível integrar este chatbot ao WhatsApp ou Telegram?

  Sim, o backend já está estruturado com FastAPI, o que permite integração com:
    - WhatsApp via Twilio ou 360Dialog API
    - Telegram via Bot API oficial

  Basta criar um webhook que conecte o canal ao endpoint `/responder`.

2. O que garante que o chatbot continuará funcionando se o site do IBGE sair do ar?

A arquitetura prevê três níveis de segurança:

1. Dados locais `.json` já armazenados (funcionam offline);
2. Fallback dinâmico entre IBGE e Wikipedia (caso uma falhe, a outra cobre);
3. Em último caso, o bot retorna uma mensagem clara informando que a fonte está temporariamente indisponível.
```
<a> <img align="right" width="90px" src="https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png">
<img align="right" width ='40px' src ='https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg'>
<img align="right" width ='40px' src ='https://raw.githubusercontent.com/devicons/devicon/refs/heads/master/icons/nextjs/nextjs-original.svg'> </a>
