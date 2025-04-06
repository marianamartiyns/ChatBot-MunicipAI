import plotly.express as px
import streamlit as st
from langchain.tools import tool
import pandas as pd

@tool
def gerar_grafico(dados: pd.DataFrame, coluna_x: str, coluna_y: str, titulo: str = "Gráfico"):
    """
    Gera um gráfico interativo utilizando Plotly e exibe no Streamlit.

    Args:
        dados (pd.DataFrame): DataFrame contendo os dados a serem plotados.
        coluna_x (str): Nome da coluna para o eixo X.
        coluna_y (str): Nome da coluna para o eixo Y.
        titulo (str): Título do gráfico.

    Returns:
        str: Mensagem indicando sucesso ou erro na geração do gráfico.
    """
    try:
        fig = px.bar(dados, x=coluna_x, y=coluna_y, title=titulo)
        st.plotly_chart(fig, use_container_width=True)
        return "Gráfico gerado com sucesso."
    except Exception as e:
        return f"Erro ao gerar gráfico: {e}"