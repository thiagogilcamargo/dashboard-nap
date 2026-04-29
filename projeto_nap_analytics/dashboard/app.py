# dashboard/app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboard.utils import (
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
# SIDEBAR COM FILTROS
# ============================================================
st.sidebar.title("🎛️ Filtros")
st.sidebar.markdown("---")

if 'Campus' in df.columns:
    campus_opcoes = ['Todos'] + sorted(df['Campus'].dropna().unique().tolist())
    campus_selecionado = st.sidebar.selectbox("🏢 Campus", campus_opcoes)
    if campus_selecionado != 'Todos':
        df = df[df['Campus'] == campus_selecionado]

if 'Período' in df.columns:
    periodo_opcoes = ['Todos'] + sorted(df['Período'].dropna().unique().tolist())
    periodo_selecionado = st.sidebar.selectbox("🌞 Período", periodo_opcoes)
    if periodo_selecionado != 'Todos':
        df = df[df['Período'] == periodo_selecionado]

if 'Faixa Etária' in df.columns:
    idade_opcoes = ['Todas'] + sorted(df['Faixa Etária'].dropna().unique().tolist())
    idade_selecionada = st.sidebar.selectbox("📅 Faixa Etária", idade_opcoes)
    if idade_selecionada != 'Todas':
        df = df[df['Faixa Etária'] == idade_selecionada]

if 'Gênero' in df.columns:
    generos = df['Gênero'].dropna().unique().tolist()
    genero_opcoes = ['Todos'] + sorted(generos)
    genero_selecionado = st.sidebar.selectbox("👥 Gênero", genero_opcoes)
    if genero_selecionado != 'Todos':
        df = df[df['Gênero'] == genero_selecionado]

if 'Semestre' in df.columns:
    semestre_opcoes = ['Todos'] + sorted(df['Semestre'].dropna().unique().tolist())
    semestre_selecionado = st.sidebar.selectbox("📚 Semestre", semestre_opcoes)
    if semestre_selecionado != 'Todos':
        df = df[df['Semestre'] == semestre_selecionado]

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
st.markdown("---")

# ============================================================
# KPIs
# ============================================================
st.subheader("📊 Visão Geral")

necessidade = df['score_necessidade'].mean() if 'score_necessidade' in df.columns else 0
suporte = df['score_suporte'].mean() if 'score_suporte' in df.columns else 0
gap = df['score_gap'].mean() if 'score_gap' in df.columns else 0
intencao = df['score_intencao'].mean() if 'score_intencao' in df.columns else 0

pct_usou = (df['Jornada'] == 'Usou NAP').mean() * 100 if 'Jornada' in df.columns else 0
pct_conhece = (df['Jornada'] == 'Conhece mas não usou').mean() * 100 if 'Jornada' in df.columns else 0
pct_nao_conhece = (df['Jornada'] == 'Não conhece NAP').mean() * 100 if 'Jornada' in df.columns else 0

col1, col2, col3, col4 = st.columns(4)
col5, col6, col7, col8 = st.columns(4)

with col1:
    st.metric("📋 Total", len(df))
with col2:
    st.metric("✅ Já usaram", f"{pct_usou:.0f}%")
with col3:
    st.metric("🎯 Necessidade", f"{necessidade:.1f}/10" if necessidade > 0 else "N/A")
with col4:
    st.metric("🏫 Suporte", f"{suporte:.1f}/10" if suporte > 0 else "N/A")
with col5:
    st.metric("📊 Gap", f"{gap:.1f}" if not pd.isna(gap) else "N/A")
with col6:
    st.metric("🎯 Intenção", f"{intencao:.1f}/10" if intencao > 0 else "N/A")
with col7:
    st.metric("👀 Conhecem mas não usaram", f"{pct_conhece:.0f}%")
with col8:
    st.metric("❌ Desconhecem", f"{pct_nao_conhece:.0f}%")

# ============================================================
# FUNIL DE ADOÇÃO
# ============================================================
st.markdown("---")
st.subheader("📊 Funil de Adoção")
if 'Jornada' in df.columns:
    funil = df['Jornada'].value_counts().reset_index()
    funil.columns = ['Status', 'Quantidade']
    fig = px.bar(funil, x='Status', y='Quantidade', color='Status', text='Quantidade')
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# SCORES POR DIMENSÃO
# ============================================================
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
    fig_scores = px.bar(df_scores, x='Dimensão', y='Score', range_y=[0,10], text='Score')
    st.plotly_chart(fig_scores, use_container_width=True)

# ============================================================
# PRIORIZAÇÃO DE PROBLEMAS
# ============================================================
st.markdown("---")
st.subheader("🎯 Priorização de Problemas")

# Calcular priorização com dados reais
problemas = []

col_info = None
for col in df.columns:
    if 'sei a quem recorrer' in col.lower():
        col_info = col
        break

if col_info:
    dados = pd.to_numeric(df[col_info], errors='coerce').dropna()
    if len(dados) > 0:
        impacto_info = 10 - dados.mean()
        problemas.append({"Problema": "Falta de informação", "Impacto": impacto_info, "Esforço": 2})

col_prec = None
for col in df.columns:
    if 'preconceito' in col.lower():
        col_prec = col
        break

if col_prec:
    dados = pd.to_numeric(df[col_prec], errors='coerce').dropna()
    if len(dados) > 0:
        impacto_prec = dados.mean()
        problemas.append({"Problema": "Preconceito", "Impacto": impacto_prec, "Esforço": 6})

if problemas:
    df_problemas = pd.DataFrame(problemas)
    df_problemas['Prioridade'] = df_problemas['Impacto'] / df_problemas['Esforço']
    df_problemas = df_problemas.sort_values('Prioridade', ascending=False)
    fig_prior = px.bar(df_problemas, x='Problema', y='Prioridade', color='Problema', text='Prioridade')
    st.plotly_chart(fig_prior, use_container_width=True)
    with st.expander("📋 Detalhamento da priorização"):
        st.dataframe(df_problemas)
else:
    st.info("Dados insuficientes para priorização")

# ============================================================
# DISTRIBUIÇÕES DEMOGRÁFICAS
# ============================================================
st.markdown("---")
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
# CAMPUS
# ============================================================
st.markdown("---")
if 'Campus' in df.columns:
    st.subheader("🏢 Distribuição por Campus")
    campus_counts = df['Campus'].value_counts().reset_index()
    campus_counts.columns = ['Campus', 'Quantidade']
    fig_campus = px.bar(campus_counts, x='Campus', y='Quantidade', color='Campus', text='Quantidade')
    st.plotly_chart(fig_campus, use_container_width=True)

# ============================================================
# INSIGHT ESTRATÉGICO
# ============================================================
st.markdown("---")
st.success("✅ Dashboard rodando com todos os componentes!")

if necessidade > 0 and suporte > 0:
    if necessidade > 7 and suporte < 5:
        st.warning(f"⚠️ **Alerta:** Alta necessidade ({necessidade:.1f}) vs baixo suporte ({suporte:.1f})")
    elif necessidade > suporte + 2:
        st.info(f"📌 **Atenção:** Necessidade ({necessidade:.1f}) é maior que o suporte percebido ({suporte:.1f})")

if pct_nao_conhece > 40:
    st.info(f"💡 **Insight:** {pct_nao_conhece:.0f}% dos alunos desconhecem o NAP. Invista em divulgação!")
