import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os
from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType
from langchain_groq import ChatGroq

from tools.plot_tool import gerar_grafico  # opcional
from tools.sidra_tool import (
    consultar_sidra,
    listar_campos_da_tabela,
    get_cod_estado, consultar_sidra_chatbot
)
from agent import agent

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from data.fetch_sidra import coletar_dados_local, carregar_municipios
from data.fetch_ibge_estados import coletar_indicadores_estaduais

# === Config inicial ===
st.set_page_config(page_title="Chatbot IBGE", layout="wide")
st.title("🤖 Chatbot IBGE")

# === Tabs ===
aba_consulta, aba_chatbot = st.tabs(["📊 Consulta por Indicador", "💬 Chatbot Inteligente"])

# === Dados auxiliares ===
tabelas_disponiveis = {
    "1419": "Produção de Leite por Município",
    "6579": "População residente por Município",
    "2938": "Produto Interno Bruto dos Municípios",
}
path_municipios = os.path.join(os.path.dirname(__file__), "..", "data", "municipios", "municipios_filtrados.txt")
municipios_lista = carregar_municipios(path_municipios)
municipios_dict = {m["nome"]: m["codigo"] for m in municipios_lista}


# === 📊 Aba de consulta tradicional ===
with aba_consulta:
    st.header("Consulta Manual ou Automática de Indicadores")
    with st.sidebar:
        st.header("🔍 Parâmetros de consulta")

        consulta_tipo = st.radio("Tipo de consulta:", ["manual", "automática (vários indicadores)"])
        nivel = st.radio("Escolha o nível territorial:", ["municipal", "estadual"])

        if nivel == "municipal":
            local = st.selectbox("Município:", options=sorted(municipios_dict.keys()))
            local_param = municipios_dict[local]
        else:
            local = st.text_input("Estado (nome ou código IBGE):", placeholder="Ex: Minas Gerais ou 31")
            local_param = get_cod_estado(local)

        if consulta_tipo == "manual":
            tabela_nome = st.selectbox("Escolha a tabela:", options=list(tabelas_disponiveis.values()))
            tabela_num = [k for k, v in tabelas_disponiveis.items() if v == tabela_nome][0]
            variaveis = st.text_input("Códigos das variáveis (opcional):", placeholder="Ex: 37, 593")

        col1, col2 = st.columns(2)
        with col1:
            consultar = st.button("🔎 Consultar")
        with col2:
            ver_campos = st.button("📄 Ver variáveis disponíveis")

    # Ver variáveis da tabela (manual)
    if ver_campos and consulta_tipo == "manual":
        st.info(f"🔍 Variáveis disponíveis na tabela {tabela_num}: {tabela_nome}")
        try:
            campos = listar_campos_da_tabela(tabela_num)
            for campo in campos:
                st.markdown(f"- {campo}")
        except Exception as e:
            st.error(f"Erro ao listar campos: {e}")

    # Executar consulta
    if consultar:
        st.subheader("📊 Resultado da Consulta")
        try:
            if consulta_tipo == "manual":
                df = consultar_sidra(tabela_num, nivel, local_param, variaveis)
            else:
                # SIDRA - Dados municipais
                df_municipio = coletar_dados_local(local_param)

                # IBGE - Indicadores estaduais
                @st.cache_data(ttl=86400)
                def get_dados_ibge():
                    from data.fetch_ibge_estados import coletar_indicadores_estaduais
                    return coletar_indicadores_estaduais()

                df_ibge = get_dados_ibge()

                # Tenta extrair a UF a partir do código do município
                uf_str = str(local_param)[:2]
                uf_map = {
                    '11': 'RO', '12': 'AC', '13': 'AM', '14': 'RR', '15': 'PA', '16': 'AP', '17': 'TO',
                    '21': 'MA', '22': 'PI', '23': 'CE', '24': 'RN', '25': 'PB', '26': 'PE', '27': 'AL',
                    '28': 'SE', '29': 'BA', '31': 'MG', '32': 'ES', '33': 'RJ', '35': 'SP', '41': 'PR',
                    '42': 'SC', '43': 'RS', '50': 'MS', '51': 'MT', '52': 'GO', '53': 'DF'
                }
                estado_sigla = uf_map.get(uf_str, None)
                dados_estado_ibge = df_ibge[df_ibge['UF'] == estado_sigla] if estado_sigla else pd.DataFrame()

                # Mostrar dados do município (SIDRA), se houver
                if not df_municipio.empty:
                    st.markdown("### 🏙️ Indicadores do Município (Fonte: SIDRA)")
                    indicadores = df_municipio["indicador"].unique()

                    for ind in indicadores:
                        df_ind = df_municipio[df_municipio["indicador"] == ind]
                        df_ind = df_ind[df_ind["Valor"] != "-"]
                        df_ind["Ano"] = pd.to_numeric(df_ind["Ano"], errors="coerce")
                        df_ind = df_ind[df_ind["Ano"].notna()]

                        if df_ind.empty:
                            continue

                        linha_mais_recente = df_ind.sort_values(by="Ano", ascending=False).iloc[0]
                        ano = int(linha_mais_recente["Ano"])
                        valor = linha_mais_recente["Valor"]

                        descritoras = [c for c in df_ind.columns if c.startswith("D") and c.endswith("N")]
                        descricoes = "\n".join([f"**{desc}:** {linha_mais_recente[desc]}" for desc in descritoras])

                        with st.container():
                            st.markdown(f"#### {ind}")
                            col1, col2 = st.columns([1, 2])
                            with col1:
                                st.metric("Valor mais recente", valor, help=f"Ano: {ano}")
                                if descricoes:
                                    st.markdown(descricoes)
                            with col2:
                                st.markdown(f"🗓️ **Ano:** {ano}")
                                tabela_info = linha_mais_recente.get("Código da Tabela", None)
                                if tabela_info:
                                    st.markdown(f"ℹ️ **Fonte:** SIDRA (Tabela {tabela_info})")
                                else:
                                    st.markdown("ℹ️ **Fonte:** SIDRA")
                                st.markdown("---")
                else:
                    st.warning("⚠️ Nenhum dado municipal encontrado no SIDRA.")

                # Mostrar dados do estado (IBGE), se houver
                if not dados_estado_ibge.empty:
                    st.markdown(f"### 📍 Indicadores do Estado ({estado_sigla}) - Fonte: ibge.gov.br")
                    for col in dados_estado_ibge.columns:
                        if col != 'UF':
                            valor = dados_estado_ibge.iloc[0][col]
                            st.metric(label=col, value=valor)
                else:
                    st.warning("⚠️ Dados estaduais do IBGE não encontrados.")
        except Exception as e:
            st.error(f"❌ Erro ao consultar dados: {e}")


# === 💬 Aba do chatbot ===
with aba_chatbot:
    st.header("💬 Converse com o Chatbot")
    st.markdown("Exemplos de perguntas:\n- Qual é o PIB de Uberlândia?\n- Me diga a população rural de Contagem\n- Qual a produção de leite em Minas Gerais?")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Digite sua pergunta...")

    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                resposta = agent.run(prompt)
                st.markdown(resposta)
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                st.session_state.chat_history.append({"role": "assistant", "content": resposta})
            except Exception as e:
                st.error(f"Erro na resposta do chatbot: {e}")
