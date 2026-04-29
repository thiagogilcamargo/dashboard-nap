import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# IMPORT CORRETO
sys.path.append(os.path.dirname(__file__))

from utils import (
    carregar_dados_brutos,
    aplicar_jornada,
    calcular_scores,
    limpar_colunas
)

st.set_page_config(page_title="NAP Analytics", layout="wide")


@st.cache_data
def carregar_e_processar():
    df = carregar_dados_brutos()
    df = aplicar_jornada(df)
    df = calcular_scores(df)
    df = limpar_colunas(df)
    return df


df = carregar_e_processar()


# ============================================================
# KPIs
# ============================================================
st.title("🧠 NAP Analytics")

st.metric("Total respostas", len(df))

st.metric("Necessidade média", round(df["score_necessidade"].mean(), 2))
st.metric("Suporte médio", round(df["score_suporte"].mean(), 2))
st.metric("Intenção média", round(df["score_intencao"].mean(), 2))

# ============================================================
# FUNIL
# ============================================================
st.subheader("Jornada")

if "Jornada" in df.columns:
    funil = df["Jornada"].value_counts().reset_index()
    funil.columns = ["Status", "Quantidade"]

    fig = px.bar(funil, x="Status", y="Quantidade", text="Quantidade")
    st.plotly_chart(fig, use_container_width=True)
