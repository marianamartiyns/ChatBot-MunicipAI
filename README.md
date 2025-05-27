# 🤖 Chatbot – Assistant for Municipal and State Indicators

> [PT/BR] Chatbot inteligente com Painel de Indicadores desenvolvido para uso interno de uma empresa privada, com o objetivo de fornecer respostas rápidas e confiáveis sobre dados públicos de municípios e estados brasileiros, além de informações institucionais da própria empresa. A solução integra scraping, APIs públicas, LLMs e uma interface interativa.

The chatbot was built using three main data sources:

- **IBGE (SIDRA and institutional website)**: the official source for demographic, social, and economic indicators, collected via API and structured scraping.
- **Company’s Institutional Database**: a JSON-based structure with Q&A about the company’s operations (data provided through the official website).

All locations are organized by IBGE code in `.json` files with normalized names.

https://github.com/user-attachments/assets/6a15b904-fa2e-4f24-8063-8d694701d1b2

### 🔨 Modeling

The model used is **LLaMA 3-8B** via **Groq**, with a temperature of 0.5 to balance accuracy and fluency.

> Response generation flow:
> 1. Identify the municipality or state mentioned.
> 2. Retrieve structured data (from SIDRA or IBGE CIDADES).
> 3. Build a prompt with real data + user question.
> 4. Send the prompt to the LLM and format the answer.
> 5. Automatically cite the source used.

Institutional questions are handled separately, using a direct search in the company’s text database.

### 🚀 Deployment

The backend was developed in **Python (FastAPI)**, with RESTful endpoints for frontend interaction and LLM communication.

The frontend was built using **Next.js**, offering an interface that allows users to:
- Browse indicators by municipality or state.
- Ask questions in natural language.
- View the source of the returned data.

The LLM is hosted on the **Groq platform**, and scraping is performed in real time, only when necessary.

> [!note]
> Hosting options include:
> - **Render ou Railway** (backend FastAPI),
> - **Vercel** (frontend Next.js), with HTTP communication (`/responder`, `/mensagem-inicial`, etc).

### 🧭 Future Improvements

- [ ] **Log questions and sources used** for future analysis and knowledge base improvements.
- [ ] **Integrate a relational database**, removing the dependency on local files.
- [ ] **Expand to new topics** (e.g., health, economy, public safety).
- [ ] **Train a lightweight fine-tuned model** based on frequently asked questions.
- [ ] **Implement a user feedback system** (👍/👎) for continuous answer improvement.

```
❓ FAQ – Frequently Asked Questions

1. Can this chatbot be integrated with WhatsApp or Telegram?

  Yes, the backend is already structured with FastAPI, which allows integration with:
    - WhatsApp via Twilio or 360Dialog API
    - Telegram via the official Bot API

  You just need to create a webhook that connects the channel to the `/responder` endpoint.

2. What ensures the chatbot will keep working if the IBGE website goes offline?

The architecture has three levels of fallback:

1. Locally stored `.json` data (works offline);
2. Dynamic fallback between IBGE and Wikipedia (if one fails, the other takes over);
3. As a last resort, the bot returns a clear message stating the source is temporarily unavailable.
```
<a> <img align="right" width="90px" src="https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png">
<img align="right" width ='40px' src ='https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg'>
<img align="right" width ='40px' src ='https://raw.githubusercontent.com/devicons/devicon/refs/heads/master/icons/nextjs/nextjs-original.svg'> </a>
