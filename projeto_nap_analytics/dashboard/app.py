# dashboard/app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    carregar_dados_brutos,
    aplicar_jornada,
    calcular_scores_dataframe,
    calcular_priorizacao,
    limpar_colunas,
    relatorio_qualidade_dados
)

st.set_page_config(page_title="NAP Analytics", layout="wide")

@st.cache_data
def carregar_e_processar():
    df = carregar_dados_brutos()
    df = aplicar_jornada(df)
    df = calcular_scores_dataframe(df)
    df = limpar_colunas(df)
    return df

df = carregar_e_processar()
df_problemas = calcular_priorizacao(df)
qualidade = relatorio_qualidade_dados(df)

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

# ============================================================
# DATA QUALITY PANEL (NOVO)
# ============================================================
with st.sidebar.expander("📊 Qualidade dos Dados"):
    st.markdown("#### Completude por pergunta")
    for col, dados in qualidade.items():
        nome_curto = col[:40] + "..." if len(col) > 40 else col
        st.metric(
            nome_curto,
            f"{dados['percentual']:.0f}%",
            help=f"{dados['valido']}/{dados['total']} respostas válidas"
        )

st.sidebar.caption(f"📊 Mostrando **{len(df)}** registros")

# ============================================================
# DASHBOARD PRINCIPAL
# ============================================================
st.title("🧠 NAP — Núcleo de Apoio Psicopedagógico")
st.markdown("### Painel de Jornada e Experiência do Aluno")
st.markdown("---")

# ============================================================
# KPIs COM CONFIANÇA
# ============================================================
st.subheader("📊 Visão Geral")

# Calcular médias (ignorando NaN)
necessidade = df['score_necessidade'].mean() if 'score_necessidade' in df.columns else np.nan
suporte = df['score_suporte'].mean() if 'score_suporte' in df.columns else np.nan
gap = df['score_gap'].mean() if 'score_gap' in df.columns else np.nan
intencao = df['score_intencao'].mean() if 'score_intencao' in df.columns else np.nan

n_necessidade_validos = df['score_necessidade'].notna().sum() if 'score_necessidade' in df.columns else 0
n_suporte_validos = df['score_suporte'].notna().sum() if 'score_suporte' in df.columns else 0
n_intencao_validos = df['score_intencao'].notna().sum() if 'score_intencao' in df.columns else 0

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
    if pd.isna(necessidade) or n_necessidade_validos < 10:
        st.metric("🎯 Necessidade", "⚠️ Dados insuficientes")
    else:
        conf = (n_necessidade_validos / len(df)) * 100
        st.metric("🎯 Necessidade", f"{necessidade:.1f}/10", help=f"Confiança: {conf:.0f}% ({n_necessidade_validos} respostas)")
with col4:
    if pd.isna(suporte) or n_suporte_validos < 10:
        st.metric("🏫 Suporte", "⚠️ Dados insuficientes")
    else:
        conf = (n_suporte_validos / len(df)) * 100
        st.metric("🏫 Suporte", f"{suporte:.1f}/10", help=f"Confiança: {conf:.0f}% ({n_suporte_validos} respostas)")
with col5:
    if pd.isna(gap):
        st.metric("📊 Gap", "⚠️ Dados insuficientes")
    else:
        st.metric("📊 Gap", f"{gap:.1f}")
with col6:
    if pd.isna(intencao) or n_intencao_validos < 10:
        st.metric("🎯 Intenção", "⚠️ Dados insuficientes")
    else:
        conf = (n_intencao_validos / len(df)) * 100
        st.metric("🎯 Intenção", f"{intencao:.1f}/10", help=f"Confiança: {conf:.0f}% ({n_intencao_validos} respostas)")
with col7:
    st.metric("👀 Conhecem", f"{pct_conhece:.0f}%")
with col8:
    st.metric("❌ Desconhecem", f"{pct_nao_conhece:.0f}%")

# Alerta de baixa qualidade
if n_necessidade_validos < len(df) * 0.3:
    st.warning(f"⚠️ Baixa confiança nos dados de Necessidade: apenas {n_necessidade_validos}/{len(df)} respostas válidas")

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
if not pd.isna(necessidade) and n_necessidade_validos >= 10:
    scores_data.append({"Dimensão": "Necessidade", "Score": necessidade, "Confiança": f"{n_necessidade_validos}/{len(df)}"})
if not pd.isna(suporte) and n_suporte_validos >= 10:
    scores_data.append({"Dimensão": "Suporte", "Score": suporte, "Confiança": f"{n_suporte_validos}/{len(df)}"})
if not pd.isna(intencao) and n_intencao_validos >= 10:
    scores_data.append({"Dimensão": "Intenção", "Score": intencao, "Confiança": f"{n_intencao_validos}/{len(df)}"})

if scores_data:
    df_scores = pd.DataFrame(scores_data)
    fig_scores = px.bar(df_scores, x='Dimensão', y='Score', range_y=[0,10], text='Score')
    st.plotly_chart(fig_scores, use_container_width=True)
    
    with st.expander("📋 Detalhamento da confiança"):
        st.dataframe(df_scores)

# ============================================================
# PRIORIZAÇÃO
# ============================================================
st.markdown("---")
st.subheader("🎯 Priorização de Problemas")
if not df_problemas.empty:
    fig_prior = px.bar(df_problemas, x='Problema', y='Prioridade', color='Prioridade', text='Prioridade')
    st.plotly_chart(fig_prior, use_container_width=True)
    with st.expander("📋 Detalhamento"):
        st.dataframe(df_problemas)

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
# INSIGHT
# ============================================================
st.markdown("---")
st.success("✅ Dashboard com Data Quality Panel!")

if not pd.isna(necessidade) and not pd.isna(suporte) and n_necessidade_validos > 10 and n_suporte_validos > 10:
    if necessidade > 7 and suporte < 5:
        st.warning(f"⚠️ **Alerta estratégico:** Alta necessidade ({necessidade:.1f}/10) mas baixo suporte percebido ({suporte:.1f}/10). Gap de {gap:.1f} pontos.")
    elif necessidade > suporte + 2:
        st.info(f"📌 **Atenção:** Necessidade ({necessidade:.1f}) é significativamente maior que o suporte percebido ({suporte:.1f}).")

if not df_problemas.empty:
    top_problema = df_problemas.iloc[0]['Problema']
    st.info(f"💡 **Insight estratégico:** O principal problema identificado é '{top_problema}'. Recomenda-se priorizar ações neste ponto.")
