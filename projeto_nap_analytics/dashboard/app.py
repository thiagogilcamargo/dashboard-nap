# dashboard/app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    carregar_dados_brutos, 
    aplicar_jornada, 
    calcular_scores_dataframe,
    calcular_priorizacao,
    limpar_colunas
)

st.set_page_config(page_title="NAP Analytics", layout="wide")

# ============================================================
# CARREGAR E PROCESSAR DADOS
# ============================================================
@st.cache_data
def carregar_e_processar():
    df = carregar_dados_brutos()
    df = aplicar_jornada(df)
    df = calcular_scores_dataframe(df)
    df = limpar_colunas(df)
    return df

df = carregar_e_processar()
df_problemas = calcular_priorizacao(df)

# ============================================================
# SIDEBAR COM FILTROS COMPLETOS
# ============================================================
st.sidebar.title("🎛️ Filtros")
st.sidebar.markdown("---")

# 1. Filtro de Campus
if 'Campus' in df.columns:
    campus_opcoes = ['Todos'] + sorted(df['Campus'].dropna().unique().tolist())
    campus_selecionado = st.sidebar.selectbox("🏢 Campus", campus_opcoes)
    if campus_selecionado != 'Todos':
        df = df[df['Campus'] == campus_selecionado]

# 2. Filtro de Período
if 'Período' in df.columns:
    periodo_opcoes = ['Todos'] + sorted(df['Período'].dropna().unique().tolist())
    periodo_selecionado = st.sidebar.selectbox("🌞 Período", periodo_opcoes)
    if periodo_selecionado != 'Todos':
        df = df[df['Período'] == periodo_selecionado]

# 3. Filtro de Faixa Etária
if 'Faixa Etária' in df.columns:
    idade_opcoes = ['Todas'] + sorted(df['Faixa Etária'].dropna().unique().tolist())
    idade_selecionada = st.sidebar.selectbox("📅 Faixa Etária", idade_opcoes)
    if idade_selecionada != 'Todas':
        df = df[df['Faixa Etária'] == idade_selecionada]

# 4. Filtro de Gênero (todos os gêneros do CSV)
if 'Gênero' in df.columns:
    generos = df['Gênero'].dropna().unique().tolist()
    genero_opcoes = ['Todos'] + sorted(generos)
    genero_selecionado = st.sidebar.selectbox("👥 Gênero", genero_opcoes)
    if genero_selecionado != 'Todos':
        df = df[df['Gênero'] == genero_selecionado]

# 5. Filtro de Semestre
if 'Semestre' in df.columns:
    semestre_opcoes = ['Todos'] + sorted(df['Semestre'].dropna().unique().tolist())
    semestre_selecionado = st.sidebar.selectbox("📚 Semestre", semestre_opcoes)
    if semestre_selecionado != 'Todos':
        df = df[df['Semestre'] == semestre_selecionado]

# 6. Filtro por Status do NAP (os 3 status)
if 'Jornada' in df.columns:
    status_opcoes = ['Todos'] + sorted(df['Jornada'].dropna().unique().tolist())
    status_selecionado = st.sidebar.selectbox("🔄 Status no NAP", status_opcoes)
    if status_selecionado != 'Todos':
        df = df[df['Jornada'] == status_selecionado]

st.sidebar.markdown("---")
st.sidebar.caption(f"📊 Mostrando **{len(df)}** registros")

# ============================================================
# DASHBOARD PRINCIPAL
# ============================================================
st.title("🧠 NAP — Núcleo de Apoio Psicopedagógico")
st.markdown("### Painel de Jornada e Experiência do Aluno")

# ============================================================
# KPIs (3 status do NAP)
# ============================================================
st.subheader("📊 Visão Geral")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("📋 Total", len(df))

with col2:
    pct_usou = (df['Jornada'] == 'Usou NAP').mean() * 100
    st.metric("✅ Usou NAP", f"{pct_usou:.0f}%")

with col3:
    pct_conhece = (df['Jornada'] == 'Conhece mas não usou').mean() * 100
    st.metric("👀 Conhece mas não usou", f"{pct_conhece:.0f}%")

with col4:
    pct_nao_conhece = (df['Jornada'] == 'Não conhece NAP').mean() * 100
    st.metric("❌ Não conhece NAP", f"{pct_nao_conhece:.0f}%")

with col5:
    if 'score_percepcao' in df.columns:
        st.metric("⭐ Percepção geral", f"{df['score_percepcao'].mean():.1f}/10")

# ============================================================
# FUNIL (3 status)
# ============================================================
if 'Jornada' in df.columns:
    st.subheader("📊 Funil de Adoção (3 status)")
    funil = df['Jornada'].value_counts().reset_index()
    funil.columns = ['Status', 'Quantidade']
    fig = px.bar(funil, x='Status', y='Quantidade', color='Status', text='Quantidade')
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# SCORES POR DIMENSÃO
# ============================================================
st.subheader("📊 Scores por Dimensão")
scores_data = []

if 'score_percepcao' in df.columns:
    scores_data.append({"Dimensão": "Percepção", "Score": df['score_percepcao'].mean()})
if 'score_intencao' in df.columns:
    scores_data.append({"Dimensão": "Intenção", "Score": df['score_intencao'].mean()})
if 'score_experiencia' in df.columns:
    exp_mean = df[df['Jornada'] == 'Usou NAP']['score_experiencia'].mean()
    if not pd.isna(exp_mean):
        scores_data.append({"Dimensão": "Experiência", "Score": exp_mean})
if 'score_acesso' in df.columns:
    acesso_mean = df[df['Jornada'] == 'Usou NAP']['score_acesso'].mean()
    if not pd.isna(acesso_mean):
        scores_data.append({"Dimensão": "Acesso", "Score": acesso_mean})

if scores_data:
    df_scores = pd.DataFrame(scores_data)
    fig_scores = px.bar(df_scores, x='Dimensão', y='Score', range_y=[0,10], text='Score')
    st.plotly_chart(fig_scores, use_container_width=True)

# ============================================================
# PRIORIZAÇÃO
# ============================================================
if not df_problemas.empty:
    st.subheader("🎯 Priorização de Problemas")
    fig_prior = px.bar(df_problemas, x='Problema', y='Prioridade', color='Prioridade', text='Prioridade')
    st.plotly_chart(fig_prior, use_container_width=True)
    
    with st.expander("📋 Detalhamento da priorização"):
        st.dataframe(df_problemas[['Problema', 'Impacto', 'Esforço', 'Prioridade']])

# ============================================================
# DISTRIBUIÇÕES DEMOGRÁFICAS
# ============================================================
st.subheader("📈 Distribuições Demográficas")

col_esq, col_meio, col_dir = st.columns(3)

with col_esq:
    if 'Faixa Etária' in df.columns:
        idade_counts = df['Faixa Etária'].value_counts().reset_index()
        idade_counts.columns = ['Faixa Etária', 'Quantidade']
        fig_id = px.pie(idade_counts, values='Quantidade', names='Faixa Etária')
        st.plotly_chart(fig_id, use_container_width=True)

with col_meio:
    if 'Gênero' in df.columns:
        genero_counts = df['Gênero'].value_counts().reset_index()
        genero_counts.columns = ['Gênero', 'Quantidade']
        fig_gen = px.pie(genero_counts, values='Quantidade', names='Gênero')
        st.plotly_chart(fig_gen, use_container_width=True)

with col_dir:
    if 'Período' in df.columns:
        periodo_counts = df['Período'].value_counts().reset_index()
        periodo_counts.columns = ['Período', 'Quantidade']
        fig_per = px.pie(periodo_counts, values='Quantidade', names='Período')
        st.plotly_chart(fig_per, use_container_width=True)

# ============================================================
# DISTRIBUIÇÃO POR CAMPUS
# ============================================================
if 'Campus' in df.columns:
    st.subheader("🏢 Distribuição por Campus")
    campus_counts = df['Campus'].value_counts().reset_index()
    campus_counts.columns = ['Campus', 'Quantidade']
    fig_campus = px.bar(campus_counts, x='Campus', y='Quantidade', color='Campus', text='Quantidade')
    st.plotly_chart(fig_campus, use_container_width=True)

# ============================================================
# INSIGHT ESTRATÉGICO
# ============================================================
st.success("✅ Dashboard completo rodando com a arquitetura correta!")

if not df_problemas.empty:
    top_problema = df_problemas.iloc[0]['Problema']
    st.info(f"💡 **Insight estratégico:** O principal problema identificado é '{top_problema}'. Recomenda-se priorizar ações neste ponto.")
