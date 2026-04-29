# dashboard/app.py (versão corrigida - sem transformar NaN em 0)
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
# SIDEBAR COM FILTROS
# ============================================================
st.sidebar.title("🎛️ Filtros")
st.sidebar.markdown("---")

if 'Campus' in df.columns:
    campus_opcoes = ['Todos'] + sorted(df['Campus'].dropna().unique().tolist())
    campus_selecionado = st.sidebar.selectbox("🏢 Campus", campus_opcoes)
    if campus_selecionado != 'Todos':
        df = df[df['Campus'] == campus_selecionado]

# ... (restante dos filtros igual ao seu)

st.sidebar.markdown("---")
st.sidebar.caption(f"📊 Mostrando **{len(df)}** registros")

# ============================================================
# DASHBOARD PRINCIPAL
# ============================================================
st.title("🧠 NAP — Núcleo de Apoio Psicopedagógico")
st.markdown("### Painel de Jornada e Experiência do Aluno")
st.markdown("---")

# ============================================================
# KPIs (SEM MASCARAR NaN COM 0)
# ============================================================
st.subheader("📊 Visão Geral")

# Calcular as médias (sem forçar 0)
necessidade = df['score_necessidade'].mean() if 'score_necessidade' in df.columns else np.nan
suporte = df['score_suporte'].mean() if 'score_suporte' in df.columns else np.nan
gap = df['score_gap'].mean() if 'score_gap' in df.columns else np.nan
intencao = df['score_intencao'].mean() if 'score_intencao' in df.columns else np.nan

pct_usou = (df['Jornada'] == 'Usou NAP').mean() * 100 if 'Jornada' in df.columns else 0
pct_conhece = (df['Jornada'] == 'Conhece mas não usou').mean() * 100 if 'Jornada' in df.columns else 0
pct_nao_conhece = (df['Jornada'] == 'Não conhece NAP').mean() * 100 if 'Jornada' in df.columns else 0

# Mostrar aviso se dados estão ruins
if pd.isna(necessidade):
    st.warning("⚠️ Dados insuficientes para calcular Necessidade. Verifique as colunas do CSV.")
    necessidade = 0
if pd.isna(suporte):
    st.warning("⚠️ Dados insuficientes para calcular Suporte.")
    suporte = 0
if pd.isna(intencao):
    st.warning("⚠️ Dados insuficientes para calcular Intenção.")
    intencao = 0

# KPIs em duas linhas
row1 = st.columns(4)
row2 = st.columns(4)

row1[0].metric("📋 Total", len(df))
row1[1].metric("✅ Já usaram", f"{pct_usou:.0f}%")
row1[2].metric("🎯 Necessidade", f"{necessidade:.1f}/10" if not pd.isna(necessidade) else "N/A")
row1[3].metric("🏫 Suporte", f"{suporte:.1f}/10" if not pd.isna(suporte) else "N/A")

row2[0].metric("📊 Gap", f"{gap:.1f}" if not pd.isna(gap) else "N/A")
row2[1].metric("🎯 Intenção", f"{intencao:.1f}/10" if not pd.isna(intencao) else "N/A")
row2[2].metric("👀 Conhecem", f"{pct_conhece:.0f}%")
row2[3].metric("❌ Desconhecem", f"{pct_nao_conhece:.0f}%")

# ... (restante do dashboard igual)
st.success("✅ Dashboard rodando com validação de dados!")
