# dashboard/app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Importa diretamente os módulos da mesma pasta
from utils import (
    carregar_dados_brutos,
    aplicar_jornada,
    calcular_scores,
    limpar_colunas,
    calcular_priorizacao,
    relatorio_qualidade_dados
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
df_problemas = calcular_priorizacao(df)

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.title("🎛️ Filtros")
st.sidebar.markdown("---")

if 'Campus' in df.columns:
    campus = st.sidebar.selectbox("🏢 Campus", ['Todos'] + sorted(df['Campus'].dropna().unique().tolist()))
    if campus != 'Todos':
        df = df[df['Campus'] == campus]

if 'Período' in df.columns:
    periodo = st.sidebar.selectbox("🌞 Período", ['Todos'] + sorted(df['Período'].dropna().unique().tolist()))
    if periodo != 'Todos':
        df = df[df['Período'] == periodo]

if 'Faixa Etária' in df.columns:
    idade = st.sidebar.selectbox("📅 Faixa Etária", ['Todas'] + sorted(df['Faixa Etária'].dropna().unique().tolist()))
    if idade != 'Todas':
        df = df[df['Faixa Etária'] == idade]

if 'Gênero' in df.columns:
    genero = st.sidebar.selectbox("👥 Gênero", ['Todos'] + sorted(df['Gênero'].dropna().unique().tolist()))
    if genero != 'Todos':
        df = df[df['Gênero'] == genero]

if 'Jornada' in df.columns:
    status = st.sidebar.selectbox("🔄 Status", ['Todos'] + sorted(df['Jornada'].dropna().unique().tolist()))
    if status != 'Todos':
        df = df[df['Jornada'] == status]

st.sidebar.markdown("---")
st.sidebar.caption(f"📊 Mostrando {len(df)} registros")

# ============================================================
# DASHBOARD
# ============================================================
st.title("🧠 NAP — Núcleo de Apoio Psicopedagógico")
st.markdown("### Painel de Jornada e Experiência do Aluno")
st.markdown("---")

st.subheader("📊 Visão Geral")

necessidade = df['score_necessidade'].mean() if 'score_necessidade' in df.columns else 0
intencao = df['score_intencao'].mean() if 'score_intencao' in df.columns else 0
pct_usou = (df['Jornada'] == 'Usou NAP').mean() * 100 if 'Jornada' in df.columns else 0
pct_conhece = (df['Jornada'] == 'Conhece mas não usou').mean() * 100 if 'Jornada' in df.columns else 0
pct_nao = (df['Jornada'] == 'Não conhece NAP').mean() * 100 if 'Jornada' in df.columns else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("📋 Total", len(df))
col2.metric("✅ Já usaram", f"{pct_usou:.0f}%")
col3.metric("🎯 Necessidade", f"{necessidade:.1f}/10" if necessidade > 0 else "N/A")
col4.metric("🎯 Intenção", f"{intencao:.1f}/10" if intencao > 0 else "N/A")
col5, col6, col7, col8 = st.columns(4)
col5.metric("👀 Conhecem", f"{pct_conhece:.0f}%")
col6.metric("❌ Desconhecem", f"{pct_nao:.0f}%")

# Funil
st.markdown("---")
st.subheader("📊 Funil de Adoção")
if 'Jornada' in df.columns:
    funil = df['Jornada'].value_counts().reset_index()
    funil.columns = ['Status', 'Quantidade']
    st.plotly_chart(px.bar(funil, x='Status', y='Quantidade', color='Status', text='Quantidade'), use_container_width=True)

st.success("✅ Dashboard rodando!")
