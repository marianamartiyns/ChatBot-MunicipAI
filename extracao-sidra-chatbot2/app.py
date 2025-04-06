import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
import os
from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType
from langchain_groq import ChatGroq
from tools.plot_tool import gerar_grafico
from tools.sidra_tool import (
    consultar_sidra,
    listar_campos_da_tabela,
    get_municipios_mg,
    get_cod_estado
)
st.set_page_config(page_title="Chatbot IBGE", layout="wide")
st.title("🤖 Chatbot IBGE com Dados Municipais")

tabelas_disponiveis = {
    "1419": "Produção de Leite por Município",
    "6579": "População residente por Município",
    "2938": "Produto Interno Bruto dos Municípios",
}

with st.sidebar:
    st.header("🔍 Parâmetros de consulta")
    tabela_nome = st.selectbox("Escolha a tabela:", options=list(tabelas_disponiveis.values()))
    tabela_num = [k for k, v in tabelas_disponiveis.items() if v == tabela_nome][0]
    nivel = st.radio("Escolha o nível territorial:", ["municipal", "estadual"])
    
    if nivel == "municipal":
        municipios = get_municipios_mg()
        local = st.selectbox("Município (MG):", options=municipios)
        local_param = municipios[local]
    else:
        local = st.text_input("Estado (nome ou código IBGE):", placeholder="Ex: Minas Gerais ou 31")
        local_param = get_cod_estado(local)

    variaveis = st.text_input("Códigos das variáveis (opcional):", placeholder="Ex: 37, 593")

    col1, col2 = st.columns(2)
    with col1:
        consultar = st.button("🔎 Consultar")
    with col2:
        ver_campos = st.button("📄 Ver variáveis disponíveis")

if ver_campos:
    st.info(f"🔍 Variáveis disponíveis na tabela {tabela_num}: {tabela_nome}")
    try:
        campos = listar_campos_da_tabela(tabela_num)
        for campo in campos:
            st.markdown(f"- {campo}")
    except Exception as e:
        st.error(f"Erro ao listar campos: {e}")

if consultar:
    st.subheader("📊 Resultado da Consulta")
    try:
        df = consultar_sidra(tabela_num, nivel, local_param, variaveis)
        if isinstance(df, str):
            st.warning(df)
        else:
            st.dataframe(df)
            st.subheader("📈 Gráfico Interativo")
            col_grafico = st.selectbox("Coluna para o gráfico:", options=df.select_dtypes(include=["float64", "int64"]).columns)
            gerar_grafico(df, coluna_x=df.columns[0], coluna_y=col_grafico, titulo=f"Gráfico de {col_grafico}")
    except Exception as e:
        st.error(f"❌ Erro ao consultar o SIDRA: {e}")