# dashboard/app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# Adiciona a raiz do projeto ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

# Priorização simplificada
df_problemas = pd.DataFrame([{"Problema": "Falta de informação", "Impacto": 7.5, "Esforço": 2, "Prioridade": 3.75}])

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

if 'Semestre' in df.columns:
    semestre = st.sidebar.selectbox("📚 Semestre", ['Todos'] + sorted(df['Semestre'].dropna().unique().tolist()))
    if semestre != 'Todos':
        df = df[df['Semestre'] == semestre]

if 'Jornada' in df.columns:
    status = st.sidebar.selectbox("🔄 Status no NAP", ['Todos'] + sorted(df['Jornada'].dropna().unique().tolist()))
    if status != 'Todos':
        df = df[df['Jornada'] == status]

st.sidebar.markdown("---")
st.sidebar.caption(f"📊 Mostrando **{len(df)}** registros")

# ============================================================
# DASHBOARD
# ============================================================
st.title("🧠 NAP — Núcleo de Apoio Psicopedagógico")
st.markdown("### Painel de Jornada e Experiência do Aluno")
st.markdown("---")

st.subheader("📊 Visão Geral")

necessidade = df['score_necessidade'].mean() if 'score_necessidade' in df.columns else 0
suporte = df['score_suporte'].mean() if 'score_suporte' in df.columns else 0
gap = df['score_gap'].mean() if 'score_gap' in df.columns else 0
intencao = df['score_intencao'].mean() if 'score_intencao' in df.columns else 0

pct_usou = (df['Jornada'] == 'Usou NAP').mean() * 100 if 'Jornada' in df.columns else 0
pct_conhece = (df['Jornada'] == 'Conhece mas não usou').mean() * 100 if 'Jornada' in df.columns else 0
pct_nao = (df['Jornada'] == 'Não conhece NAP').mean() * 100 if 'Jornada' in df.columns else 0

col1, col2, col3, col4 = st.columns(4)
col5, col6, col7, col8 = st.columns(4)

col1.metric("📋 Total", len(df))
col2.metric("✅ Já usaram", f"{pct_usou:.0f}%")
col3.metric("🎯 Necessidade", f"{necessidade:.1f}/10" if necessidade > 0 else "N/A")
col4.metric("🏫 Suporte", f"{suporte:.1f}/10" if suporte > 0 else "N/A")
col5.metric("📊 Gap", f"{gap:.1f}" if not pd.isna(gap) and gap != 0 else "N/A")
col6.metric("🎯 Intenção", f"{intencao:.1f}/10" if intencao > 0 else "N/A")
col7.metric("👀 Conhecem", f"{pct_conhece:.0f}%")
col8.metric("❌ Desconhecem", f"{pct_nao:.0f}%")

# Funil
st.markdown("---")
st.subheader("📊 Funil de Adoção")
if 'Jornada' in df.columns:
    funil = df['Jornada'].value_counts().reset_index()
    funil.columns = ['Status', 'Quantidade']
    fig = px.bar(funil, x='Status', y='Quantidade', color='Status', text='Quantidade')
    st.plotly_chart(fig, use_container_width=True)

# Scores
st.markdown("---")
st.subheader("📊 Scores por Dimensão")
scores_data = []
if necessidade > 0:
    scores_data.append({"Dimensão": "Necessidade", "Score": necessidade})
if suporte > 0:
    scores_data.append({"Dimensão": "Suporte", "Score": suporte})
if intencao > 0:
    scores_data.append({"Dimensão": "Intenção", "Score": intencao})

if scores_data:
    df_scores = pd.DataFrame(scores_data)
    fig = px.bar(df_scores, x='Dimensão', y='Score', range_y=[0,10], text='Score')
    st.plotly_chart(fig, use_container_width=True)

# Priorização
st.markdown("---")
st.subheader("🎯 Priorização de Problemas")
if not df_problemas.empty:
    fig = px.bar(df_problemas, x='Problema', y='Prioridade', color='Prioridade', text='Prioridade')
    st.plotly_chart(fig, use_container_width=True)

# Demografia
st.markdown("---")
st.subheader("📈 Distribuições Demográficas")
col_a, col_b, col_c = st.columns(3)

with col_a:
    if 'Faixa Etária' in df.columns:
        idade_counts = df['Faixa Etária'].value_counts().reset_index()
        idade_counts.columns = ['Faixa Etária', 'Quantidade']
        fig = px.pie(idade_counts, values='Quantidade', names='Faixa Etária')
        st.plotly_chart(fig, use_container_width=True)

with col_b:
    if 'Gênero' in df.columns:
        genero_counts = df['Gênero'].value_counts().reset_index()
        genero_counts.columns = ['Gênero', 'Quantidade']
        fig = px.pie(genero_counts, values='Quantidade', names='Gênero')
        st.plotly_chart(fig, use_container_width=True)

with col_c:
    if 'Período' in df.columns:
        periodo_counts = df['Período'].value_counts().reset_index()
        periodo_counts.columns = ['Período', 'Quantidade']
        fig = px.pie(periodo_counts, values='Quantidade', names='Período')
        st.plotly_chart(fig, use_container_width=True)

# Campus
st.markdown("---")
if 'Campus' in df.columns:
    st.subheader("🏢 Distribuição por Campus")
    campus_counts = df['Campus'].value_counts().reset_index()
    campus_counts.columns = ['Campus', 'Quantidade']
    fig = px.bar(campus_counts, x='Campus', y='Quantidade', color='Campus', text='Quantidade')
    st.plotly_chart(fig, use_container_width=True)

st.success("✅ Dashboard rodando!")
