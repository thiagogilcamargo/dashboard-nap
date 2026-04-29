import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# ============================================================
# 🔴 FIX IMPORT STREAMLIT CLOUD
# ============================================================
sys.path.append(os.path.dirname(__file__))

from utils import (
    carregar_dados_brutos,
    aplicar_jornada,
    calcular_scores,
    limpar_colunas
)

st.set_page_config(page_title="NAP Analytics", layout="wide")

# ============================================================
# CARREGAMENTO
# ============================================================
@st.cache_data
def carregar_e_processar():
    df = carregar_dados_brutos()
    df = aplicar_jornada(df)
    df = calcular_scores(df)
    df = limpar_colunas(df)
    return df

df = carregar_e_processar()

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.title("🎛️ Filtros")

if 'Campus' in df.columns:
    campus = st.sidebar.selectbox("Campus", ["Todos"] + sorted(df["Campus"].dropna().unique()))
    if campus != "Todos":
        df = df[df["Campus"] == campus]

if 'Período' in df.columns:
    periodo = st.sidebar.selectbox("Período", ["Todos"] + sorted(df["Período"].dropna().unique()))
    if periodo != "Todos":
        df = df[df["Período"] == periodo]

if 'Faixa Etária' in df.columns:
    idade = st.sidebar.selectbox("Faixa Etária", ["Todas"] + sorted(df["Faixa Etária"].dropna().unique()))
    if idade != "Todas":
        df = df[df["Faixa Etária"] == idade]

if 'Gênero' in df.columns:
    genero = st.sidebar.selectbox("Gênero", ["Todos"] + sorted(df["Gênero"].dropna().unique()))
    if genero != "Todos":
        df = df[df["Gênero"] == genero]

if 'Jornada' in df.columns:
    status = st.sidebar.selectbox("Jornada NAP", ["Todos"] + sorted(df["Jornada"].dropna().unique()))
    if status != "Todos":
        df = df[df["Jornada"] == status]

st.sidebar.caption(f"📊 Registros: {len(df)}")

# ============================================================
# DASHBOARD
# ============================================================
st.title("🧠 NAP Analytics")
st.markdown("---")

# KPIs
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total respostas", len(df))
col2.metric("Necessidade média", f"{df['score_necessidade'].mean():.2f}")
col3.metric("Suporte médio", f"{df['score_suporte'].mean():.2f}" if 'score_suporte' in df else "N/A")
col4.metric("Intenção média", f"{df['score_intencao'].mean():.2f}")

# ============================================================
# FUNIL
# ============================================================
st.subheader("📊 Jornada do Aluno")

if "Jornada" in df.columns:
    funil = df["Jornada"].value_counts().reset_index()
    funil.columns = ["Status", "Quantidade"]

    fig = px.bar(funil, x="Status", y="Quantidade", text="Quantidade")
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# GRAFICO SIMPLES DE SCORE
# ============================================================
st.subheader("📈 Scores")

scores = pd.DataFrame({
    "Dimensão": ["Necessidade", "Intenção"],
    "Score": [
        df["score_necessidade"].mean(),
        df["score_intencao"].mean()
    ]
})

fig2 = px.bar(scores, x="Dimensão", y="Score", text="Score", range_y=[0,10])
st.plotly_chart(fig2, use_container_width=True)

st.success("Dashboard funcionando 🚀")
