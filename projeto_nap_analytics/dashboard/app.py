# dashboard/app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sys
import os
from datetime import datetime
import base64

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
# FUNÇÃO PARA EXPORTAR HTML
# ============================================================
def gerar_html_relatorio():
    necessidade = df['score_necessidade'].mean() if 'score_necessidade' in df.columns else 0
    suporte = df['score_suporte'].mean() if 'score_suporte' in df.columns else 0
    gap = df['score_gap'].mean() if 'score_gap' in df.columns else 0
    intencao = df['score_intencao'].mean() if 'score_intencao' in df.columns else 0
    pct_usou = (df['Jornada'] == 'Usou NAP').mean() * 100 if 'Jornada' in df.columns else 0
    pct_conhece = (df['Jornada'] == 'Conhece mas não usou').mean() * 100 if 'Jornada' in df.columns else 0
    pct_nao = (df['Jornada'] == 'Não conhece NAP').mean() * 100 if 'Jornada' in df.columns else 0
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Relatório NAP</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
            h1 {{ color: #2c3e50; text-align: center; }}
            h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
            .metric-card {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #3498db; }}
            .metric-value {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
            .warning {{ color: #e74c3c; font-weight: bold; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #3498db; color: white; }}
            .footer {{ text-align: center; margin-top: 30px; font-size: 12px; color: #7f8c8d; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧠 NAP - Relatório Executivo</h1>
            <p style="text-align: center">Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            
            <h2>📊 Métricas Principais</h2>
            <div class="metric-card"><strong>Total de respondentes:</strong> <span class="metric-value">{len(df)}</span></div>
            <div class="metric-card"><strong>Já usaram o NAP:</strong> <span class="metric-value">{pct_usou:.0f}%</span></div>
            <div class="metric-card"><strong>Necessidade de apoio:</strong> <span class="metric-value">{necessidade:.1f}/10</span></div>
            <div class="metric-card"><strong>Suporte percebido:</strong> <span class="metric-value">{suporte:.1f}/10</span></div>
            <div class="metric-card"><strong>Gap:</strong> <span class="metric-value warning">{gap:.1f}</span></div>
            <div class="metric-card"><strong>Intenção de uso:</strong> <span class="metric-value">{intencao:.1f}/10</span></div>
            <div class="metric-card"><strong>Desconhecem o NAP:</strong> <span class="metric-value warning">{pct_nao:.0f}%</span></div>
            
            <h2>💡 Recomendações</h2>
            <ul>
                <li>🚨 Campanha de divulgação do NAP ({pct_nao:.0f}% desconhecem)</li>
                <li>📢 Comunicar os serviços oferecidos</li>
                <li>📊 Reduzir gap de {gap:.1f} pontos</li>
            </ul>
            
            <div class="footer">Relatório gerado automaticamente</div>
        </div>
    </body>
    </html>
    """
    return html

# ============================================================
# SIDEBAR
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

# Exportar Relatório HTML
html_report = gerar_html_relatorio()
b64 = base64.b64encode(html_report.encode()).decode()
href = f'<a href="data:text/html;base64,{b64}" download="relatorio_nap.html" style="text-decoration: none;"><button style="background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">📄 Baixar Relatório (HTML)</button></a>'
st.sidebar.markdown(href, unsafe_allow_html=True)

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
    st.metric("🎯 Necessidade", f"{necessidade:.1f}/10")
with col4:
    st.metric("🏫 Suporte", f"{suporte:.1f}/10")
with col5:
    st.metric("📊 Gap", f"{gap:.1f}")
with col6:
    st.metric("🎯 Intenção", f"{intencao:.1f}/10")
with col7:
    st.metric("👀 Conhecem", f"{pct_conhece:.0f}%")
with col8:
    st.metric("❌ Desconhecem", f"{pct_nao_conhece:.0f}%")

# ============================================================
# HEATMAP
# ============================================================
st.markdown("---")
st.subheader("📊 Matriz de Correlação")

cols_correlacao = [
    "Já senti necessidade de apoio emocional durante a graduação.",
    "Eu me sentiria confortável em procurar ajuda dentro da instituição.",
    "Eu sinto que há suporte suficiente para dificuldades emocionais na faculdade.",
    "Acredito que serviços de apoio podem melhorar a experiência acadêmica dos alunos.",
    "Eu já pensei em utilizar o NAP (Núcleo de Apoio Psicopedagógico) em algum momento.",
    "Tenho confiança na confidencialidade do atendimento oferecido pelo NAP (Núcleo de Apoio Psicopedagógico)."
]

nomes_curtos = {
    "Já senti necessidade de apoio emocional durante a graduação.": "Necessidade",
    "Eu me sentiria confortável em procurar ajuda dentro da instituição.": "Conforto",
    "Eu sinto que há suporte suficiente para dificuldades emocionais na faculdade.": "Suporte",
    "Acredito que serviços de apoio podem melhorar a experiência acadêmica dos alunos.": "Crença",
    "Eu já pensei em utilizar o NAP (Núcleo de Apoio Psicopedagógico) em algum momento.": "Intenção",
    "Tenho confiança na confidencialidade do atendimento oferecido pelo NAP (Núcleo de Apoio Psicopedagógico).": "Confiança"
}

cols_existentes = [col for col in cols_correlacao if col in df.columns]

if len(cols_existentes) >= 2:
    corr_matrix = df[cols_existentes].corr()
    corr_matrix = corr_matrix.rename(index=nomes_curtos, columns=nomes_curtos)
    fig_corr = px.imshow(corr_matrix, text_auto='.2f', aspect='auto', color_continuous_scale='RdBu_r', zmin=-1, zmax=1)
    fig_corr.update_layout(height=500)
    st.plotly_chart(fig_corr, use_container_width=True)

# ============================================================
# COMPARAÇÃO CAMPI
# ============================================================
st.markdown("---")
st.subheader("🏢 Comparação entre Campi")

if 'Campus' in df.columns and len(df['Campus'].unique()) > 1:
    campi_comparacao = df.groupby('Campus').agg({
        'score_necessidade': 'mean',
        'score_suporte': 'mean',
        'score_intencao': 'mean'
    }).reset_index()
    campi_comparacao.columns = ['Campus', 'Necessidade', 'Suporte', 'Intenção']
    
    fig_campi = go.Figure()
    fig_campi.add_trace(go.Bar(name='Necessidade', x=campi_comparacao['Campus'], y=campi_comparacao['Necessidade'], text=campi_comparacao['Necessidade'].round(1), textposition='auto', marker_color='#e74c3c'))
    fig_campi.add_trace(go.Bar(name='Suporte', x=campi_comparacao['Campus'], y=campi_comparacao['Suporte'], text=campi_comparacao['Suporte'].round(1), textposition='auto', marker_color='#3498db'))
    fig_campi.add_trace(go.Bar(name='Intenção', x=campi_comparacao['Campus'], y=campi_comparacao['Intenção'], text=campi_comparacao['Intenção'].round(1), textposition='auto', marker_color='#2ecc71'))
    fig_campi.update_layout(barmode='group', yaxis_range=[0, 10])
    st.plotly_chart(fig_campi, use_container_width=True)

# ============================================================
# EVOLUÇÃO POR SEMESTRE
# ============================================================
st.markdown("---")
st.subheader("📚 Evolução por Semestre")

if 'Semestre' in df.columns:
    df['Semestre_Num'] = df['Semestre'].str.extract(r'(\d+)').astype(float)
    evolucao = df.groupby('Semestre_Num').agg({
        'score_necessidade': 'mean',
        'score_suporte': 'mean',
        'score_intencao': 'mean'
    }).reset_index().dropna()
    
    if len(evolucao) >= 2:
        fig_evolucao = go.Figure()
        fig_evolucao.add_trace(go.Scatter(x=evolucao['Semestre_Num'], y=evolucao['score_necessidade'], mode='lines+markers', name='Necessidade', line=dict(color='#e74c3c', width=3)))
        fig_evolucao.add_trace(go.Scatter(x=evolucao['Semestre_Num'], y=evolucao['score_suporte'], mode='lines+markers', name='Suporte', line=dict(color='#3498db', width=3)))
        fig_evolucao.add_trace(go.Scatter(x=evolucao['Semestre_Num'], y=evolucao['score_intencao'], mode='lines+markers', name='Intenção', line=dict(color='#2ecc71', width=3)))
        fig_evolucao.update_layout(yaxis_range=[0, 10])
        st.plotly_chart(fig_evolucao, use_container_width=True)
        
        primeiro_sup = evolucao.iloc[0]['score_suporte']
        ultimo_sup = evolucao.iloc[-1]['score_suporte']
        if ultimo_sup < primeiro_sup:
            st.warning(f"📉 Percepção de suporte caiu {primeiro_sup - ultimo_sup:.1f} pontos ao longo dos semestres")

# ============================================================
# SCORES POR DIMENSÃO
# ============================================================
st.markdown("---")
st.subheader("📊 Scores por Dimensão")

scores_data = []
if necessidade > 0:
    scores_data.append({"Dimensão": "Necessidade", "Score": necessidade, "Descrição": "O quanto o aluno precisa de apoio"})
if suporte > 0:
    scores_data.append({"Dimensão": "Suporte", "Score": suporte, "Descrição": "O quanto a faculdade oferece apoio"})
if intencao > 0:
    scores_data.append({"Dimensão": "Intenção", "Score": intencao, "Descrição": "Disposição para usar o NAP"})

if scores_data:
    df_scores = pd.DataFrame(scores_data)
    fig_scores = px.bar(df_scores, x='Dimensão', y='Score', range_y=[0,10], text='Score', color='Dimensão')
    fig_scores.update_layout(showlegend=False)
    st.plotly_chart(fig_scores, use_container_width=True)

# ============================================================
# PRIORIZAÇÃO
# ============================================================
st.markdown("---")
st.subheader("🎯 Priorização de Problemas")

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

if gap > 3:
    problemas.append({"Problema": f"Gap de {gap:.1f} pontos", "Impacto": gap, "Esforço": 5})

if problemas:
    df_problemas = pd.DataFrame(problemas)
    df_problemas['Prioridade'] = df_problemas['Impacto'] / df_problemas['Esforço']
    df_problemas = df_problemas.sort_values('Prioridade', ascending=False)
    
    fig_prior = px.bar(df_problemas, x='Problema', y='Prioridade', color='Problema', text='Prioridade')
    st.plotly_chart(fig_prior, use_container_width=True)
    
    with st.expander("📋 Detalhamento"):
        st.dataframe(df_problemas)

# ============================================================
# FUNIL
# ============================================================
st.markdown("---")
st.subheader("📊 Funil de Adoção")
if 'Jornada' in df.columns:
    funil = df['Jornada'].value_counts().reset_index()
    funil.columns = ['Status', 'Quantidade']
    fig = px.bar(funil, x='Status', y='Quantidade', color='Status', text='Quantidade')
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# DISTRIBUIÇÕES
# ============================================================
st.markdown("---")
st.subheader("📈 Distribuições Demográficas")

col_esq, col_meio, col_dir = st.columns(3)

with col_esq:
    if 'Faixa Etária' in df.columns:
        idade = df['Faixa Etária'].value_counts().reset_index()
        idade.columns = ['Faixa Etária', 'Quantidade']
        fig = px.pie(idade, values='Quantidade', names='Faixa Etária')
        st.plotly_chart(fig, use_container_width=True)

with col_meio:
    if 'Gênero' in df.columns:
        genero = df['Gênero'].value_counts().reset_index()
        genero.columns = ['Gênero', 'Quantidade']
        fig = px.pie(genero, values='Quantidade', names='Gênero')
        st.plotly_chart(fig, use_container_width=True)

with col_dir:
    if 'Período' in df.columns:
        periodo = df['Período'].value_counts().reset_index()
        periodo.columns = ['Período', 'Quantidade']
        fig = px.pie(periodo, values='Quantidade', names='Período')
        st.plotly_chart(fig, use_container_width=True)

# ============================================================
# CAMPUS
# ============================================================
st.markdown("---")
if 'Campus' in df.columns:
    st.subheader("🏢 Distribuição por Campus")
    campus = df['Campus'].value_counts().reset_index()
    campus.columns = ['Campus', 'Quantidade']
    fig = px.bar(campus, x='Campus', y='Quantidade', color='Campus', text='Quantidade')
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# INSIGHT
# ============================================================
st.markdown("---")
st.success("✅ Dashboard rodando!")

if necessidade > 0 and suporte > 0:
    if necessidade > 7 and suporte < 5:
        st.warning(f"⚠️ Alta necessidade ({necessidade:.1f}) vs baixo suporte ({suporte:.1f})")

if pct_nao_conhece > 40:
    st.info(f"💡 {pct_nao_conhece:.0f}% desconhecem o NAP")
