# ibge_app.py
import streamlit as st
import pandas as pd
import os

from agent import agent
from tools.sidra_tool import (
    consultar_sidra,
    listar_campos_da_tabela,
    get_cod_estado
)
from data.fetch_sidra import coletar_dados_local, carregar_municipios
from data.fetch_ibge_estados import coletar_indicadores_estaduais
from data.fetch_ibge_municipios import extrair_dados_municipio
from data.fetch_sidra import get_tabelas_disponiveis

# --- Configuração geral ---
st.set_page_config(page_title="Chatbot IBGE", layout="wide")
st.title("🤖 Chatbot de Indicadores Públicos - IBGE")

# --- Carregamento de dados auxiliares ---
TABELAS_DISPONIVEIS = {
    "1419": "Produção de Leite por Município",
    "6579": "População residente por Município",
    "2938": "Produto Interno Bruto dos Municípios",
}
TABELAS_DISPONIVEIS.update(get_tabelas_disponiveis())
TABELAS_DISPONIVEIS.update({ 
    k: f"{v} (tabela {k})" for k, v in get_tabelas_disponiveis().items()
})

CAMINHO_MUNICIPIOS = os.path.join(os.path.dirname(__file__), "..", "data", "municipios", "municipios_filtrados.txt")
MUNICIPIOS = carregar_municipios(CAMINHO_MUNICIPIOS)
MUNICIPIOS_DICT = {m["nome"]: m["codigo"] for m in MUNICIPIOS}


# --- Abas principais ---
aba_consulta, aba_chatbot = st.tabs(["📊 Consulta de Indicadores", "💬 Chatbot Inteligente"])

# === ABA 1: CONSULTA ===
with aba_consulta:
    st.subheader("🎯 Faça uma busca manual ou automática por indicadores do IBGE")

    with st.sidebar:
        st.header("Parâmetros de Consulta")
        consulta_tipo = st.radio("Tipo de consulta:", ["manual", "automática (vários indicadores)"])
        nivel = st.radio("Nível territorial:", ["municipal", "estadual"])

        if nivel == "municipal":
            local = st.selectbox("Município:", sorted(MUNICIPIOS_DICT.keys()))
            local_param = MUNICIPIOS_DICT[local]
        else:
            local = st.text_input("Estado (nome ou código IBGE):", placeholder="Ex: São Paulo ou 35")
            local_param = get_cod_estado(local)

        if consulta_tipo == "manual":
            tabela_nome = st.selectbox("Tabela:", sorted(TABELAS_DISPONIVEIS.values()))
            tabela_num = next(k for k, v in TABELAS_DISPONIVEIS.items() if v == tabela_nome)
            variaveis = st.text_input("Variáveis (opcional):", placeholder="Ex: 37, 593")

        col1, col2 = st.columns(2)
        consultar = col1.button("🔎 Consultar")
        ver_campos = col2.button("📄 Ver tabela")

    if ver_campos and consulta_tipo == "manual":
        with st.expander(f"📘 Variáveis disponíveis na tabela {tabela_num}"):
            try:
                campos = listar_campos_da_tabela(tabela_num)
                for campo in campos:
                    st.markdown(f"- {campo}")
            except Exception as e:
                st.error(f"Erro ao listar variáveis: {e}")

    if consultar:
        st.subheader(" -> Resultados da Consulta")
        try:
            if consulta_tipo == "manual":
                df = consultar_sidra(tabela_num, nivel, local_param, variaveis)
                st.dataframe(df)
            else:
                df_municipio = coletar_dados_local(local_param)

                @st.cache_data(ttl=86400)
                def get_dados_estado():
                    return coletar_indicadores_estaduais()

                df_ibge = get_dados_estado()
                uf_str = str(local_param)[:2]
                uf_map = {
                    '11': 'RO', '12': 'AC', '13': 'AM', '14': 'RR', '15': 'PA', '16': 'AP', '17': 'TO',
                    '21': 'MA', '22': 'PI', '23': 'CE', '24': 'RN', '25': 'PB', '26': 'PE', '27': 'AL',
                    '28': 'SE', '29': 'BA', '31': 'MG', '32': 'ES', '33': 'RJ', '35': 'SP', '41': 'PR',
                    '42': 'SC', '43': 'RS', '50': 'MS', '51': 'MT', '52': 'GO', '53': 'DF'
                }
                sigla = uf_map.get(uf_str)

                # ----- MUNICÍPIO (Site do IBGE) -----
                st.divider()
                st.success("🏛️ Indicadores Municipais Adicionais (Fonte: ibge.gov.br)")

                try:
                    nome_municipio_limpo = local.split(" (")[0]  # Remove o estado entre parênteses
                    dados_site_ibge = extrair_dados_municipio(sigla.lower(), nome_municipio_limpo)

                    if "erro" in dados_site_ibge:
                        st.warning(f"⚠️ Não foi possível acessar os dados do site IBGE: {dados_site_ibge['erro']}")
                    else:
                        chaves_uteis = [(k, v) for k, v in dados_site_ibge.items() if k not in ["Município", "UF", "Fonte"]]

                        for k, v in chaves_uteis:
                            st.markdown(f"<h3 style='margin-bottom: 0;'>{k}</h3>", unsafe_allow_html=True)
                            st.markdown(f"<span style='font-size:20px; color:#2E95D3;'>{v}</span>", unsafe_allow_html=True)
                            st.markdown("<hr>", unsafe_allow_html=True)

                        st.caption(f"🔗 [Ver mais no site do IBGE]({dados_site_ibge['Fonte']})")

                except Exception as e:
                    st.error(f"Erro ao extrair dados do site do IBGE: {e}")

                # ----- ESTADUAL (Site do IBGE) -----
                dados_estado = df_ibge[df_ibge['UF'] == sigla] if sigla else pd.DataFrame()
                if not dados_estado.empty:
                    st.success(f"📍 Indicadores Estaduais ({sigla}) - Fonte: ibge.gov.br")

                    for col in dados_estado.columns:
                        if col != 'UF':
                            valor = dados_estado.iloc[0][col]
                            st.markdown(f"<h4 style='margin-bottom: 0;'>{col}</h4>", unsafe_allow_html=True)
                            st.markdown(f"<span style='font-size:20px; color:#2E95D3;'>{valor}</span>", unsafe_allow_html=True)
                            st.markdown("<hr>", unsafe_allow_html=True)

                    # Link para a página do estado no site do IBGE
                    estado_url = f"https://www.ibge.gov.br/cidades-e-estados/{sigla.lower()}.html"
                    st.caption(f"🔗 [Ver mais no site do IBGE]({estado_url})")
                else:
                    st.warning("⚠️ Indicadores estaduais não disponíveis.")

        except Exception as e:
            st.error(f"❌ Erro ao consultar dados: {e}")


# === ABA 2: CHATBOT ===
with aba_chatbot:
    st.subheader("💬 Converse com o Chatbot sobre dados públicos")
    st.markdown("Exemplos:\n- Qual o PIB de Uberlândia?\n- População de Contagem?\n- Leite produzido em Minas Gerais?")

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
