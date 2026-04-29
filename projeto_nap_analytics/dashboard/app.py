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
# SIDEBAR COM FILTROS (idêntico ao seu, mantido)
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

# ============================================================
# KPIS (COM NECESSIDADE, SUPORTE E GAP)
# ============================================================
st.subheader("📊 Visão Geral")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📋 Total", len(df))

with col2:
    pct_usou = (df['Jornada'] == 'Usou NAP').mean() * 100
    st.metric("✅ Já usaram", f"{pct_usou:.0f}%")

with col3:
    if 'score_necessidade' in df.columns and df['score_necessidade'].notna().any():
        st.metric("🎯 Necessidade de apoio", f"{df['score_necessidade'].mean():.1f}/10")
    else:
        st.metric("🎯 Necessidade de apoio", "⚠️ Erro")

with col4:
    if 'score_suporte' in df.columns and df['score_suporte'].notna().any():
        st.metric("🏫 Suporte percebido", f"{df['score_suporte'].mean():.1f}/10")
    else:
        st.metric("🏫 Suporte percebido", "⚠️ Erro")

col5, col6, col7, col8 = st.columns(4)

with col5:
    if 'score_gap' in df.columns and df['score_gap'].notna().any():
        gap = df['score_gap'].mean()
        cor = "🔴" if gap > 3 else "🟡" if gap > 1 else "🟢"
        st.metric(f"{cor} Gap (Necessidade - Suporte)", f"{gap:.1f}")
    else:
        st.metric("📊 Gap", "⚠️ Erro")

with col6:
    if 'score_intencao' in df.columns and df['score_intencao'].notna().any():
        st.metric("🎯 Intenção de uso", f"{df['score_intencao'].mean():.1f}/10")
    else:
        st.metric("🎯 Intenção de uso", "⚠️ Erro")

with col7:
    pct_conhece = (df['Jornada'] == 'Conhece mas não usou').mean() * 100
    st.metric("👀 Conhecem mas não usaram", f"{pct_conhece:.0f}%")

with col8:
    pct_nao_conhece = (df['Jornada'] == 'Não conhece NAP').mean() * 100
    st.metric("❌ Desconhecem", f"{pct_nao_conhece:.0f}%")

# ============================================================
# FUNIL DE ADOÇÃO
# ============================================================
if 'Jornada' in df.columns:
    st.subheader("📊 Funil de Adoção")
    funil = df['Jornada'].value_counts().reset_index()
    funil.columns = ['Status', 'Quantidade']
    fig = px.bar(funil, x='Status', y='Quantidade', color='Status', text='Quantidade')
    st.plotly_chart(fig, width='stretch')

# ============================================================
# SCORES POR DIMENSÃO (COM NECESSIDADE E SUPORTE)
# ============================================================
st.subheader("📊 Scores por Dimensão")
scores_data = []

if 'score_necessidade' in df.columns and df['score_necessidade'].notna().any():
    scores_data.append({"Dimensão": "Necessidade", "Score": df['score_necessidade'].mean()})
if 'score_suporte' in df.columns and df['score_suporte'].notna().any():
    scores_data.append({"Dimensão": "Suporte percebido", "Score": df['score_suporte'].mean()})
if 'score_gap' in df.columns and df['score_gap'].notna().any():
    scores_data.append({"Dimensão": "Gap (problema)", "Score": df['score_gap'].mean()})
if 'score_intencao' in df.columns and df['score_intencao'].notna().any():
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
    st.plotly_chart(fig_scores, width='stretch')
else:
    st.info("📊 Nenhum score disponível.")

# ============================================================
# PRIORIZAÇÃO
# ============================================================
if not df_problemas.empty:
    st.subheader("🎯 Priorização de Problemas")
    fig_prior = px.bar(df_problemas, x='Problema', y='Prioridade', color='Prioridade', text='Prioridade')
    st.plotly_chart(fig_prior, width='stretch')
    
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
        st.plotly_chart(fig_id, width='stretch')

with col_meio:
    if 'Gênero' in df.columns:
        genero_counts = df['Gênero'].value_counts().reset_index()
        genero_counts.columns = ['Gênero', 'Quantidade']
        fig_gen = px.pie(genero_counts, values='Quantidade', names='Gênero')
        st.plotly_chart(fig_gen, width='stretch')

with col_dir:
    if 'Período' in df.columns:
        periodo_counts = df['Período'].value_counts().reset_index()
        periodo_counts.columns = ['Período', 'Quantidade']
        fig_per = px.pie(periodo_counts, values='Quantidade', names='Período')
        st.plotly_chart(fig_per, width='stretch')

# ============================================================
# CAMPUS
# ============================================================
if 'Campus' in df.columns:
    st.subheader("🏢 Distribuição por Campus")
    campus_counts = df['Campus'].value_counts().reset_index()
    campus_counts.columns = ['Campus', 'Quantidade']
    fig_campus = px.bar(campus_counts, x='Campus', y='Quantidade', color='Campus', text='Quantidade')
    st.plotly_chart(fig_campus, width='stretch')

# ============================================================
# INSIGHT ESTRATÉGICO
# ============================================================
st.success("✅ Dashboard completo com Necessidade vs Suporte!")

if not df_problemas.empty:
    top_problema = df_problemas.iloc[0]['Problema']
    st.info(f"💡 **Insight estratégico:** O principal problema identificado é '{top_problema}'. Recomenda-se priorizar ações neste ponto.")

# Insight sobre o gap
if 'score_gap' in df.columns and df['score_gap'].notna().any():
    gap_medio = df['score_gap'].mean()
    if gap_medio > 3:
        st.warning(f"⚠️ **Alerta:** O gap entre necessidade ({df['score_necessidade'].mean():.1f}) e suporte percebido ({df['score_suporte'].mean():.1f}) é de {gap_medio:.1f} pontos.")
    elif gap_medio > 1:
        st.info(f"📌 **Atenção:** Diferença de {gap_medio:.1f} pontos entre necessidade e suporte.")
    else:
        st.success(f"✅ **Bom:** Suporte alinhado com necessidade (gap de {gap_medio:.1f} pontos).")
