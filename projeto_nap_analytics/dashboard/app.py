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
# FUNÇÃO PARA GERAR HTML (RELATÓRIO)
# ============================================================
def gerar_html_relatorio(df):
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
            .warning {{ color: #e74c3c; }}
            .footer {{ text-align: center; margin-top: 30px; font-size: 12px; color: #7f8c8d; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧠 NAP - Relatório Executivo</h1>
            <p style="text-align: center">Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            <div class="metric-card"><strong>Total:</strong> {len(df)} alunos</div>
            <div class="metric-card"><strong>Usaram o NAP:</strong> {pct_usou:.0f}%</div>
            <div class="metric-card"><strong>Necessidade:</strong> {necessidade:.1f}/10</div>
            <div class="metric-card"><strong>Suporte:</strong> {suporte:.1f}/10</div>
            <div class="metric-card"><strong>Gap:</strong> {gap:.1f}</div>
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
html_report = gerar_html_relatorio(df)
b64 = base64.b64encode(html_report.encode()).decode()
href = f'<a href="data:text/html;base64,{b64}" download="relatorio_nap.html" style="text-decoration: none;"><button style="background-color: #e74c3c; color: white; padding: 10px; border: none; border-radius: 5px; cursor: pointer; width: 100%;">📄 Relatório</button></a>'
st.sidebar.markdown(href, unsafe_allow_html=True)

# Exportar CSV
csv = df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="📥 Baixar dados (CSV)",
    data=csv,
    file_name=f"nap_dados_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
    mime="text/csv",
)

st.sidebar.caption(f"📊 {len(df)} registros")

# ============================================================
# DASHBOARD
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
pct_nao = (df['Jornada'] == 'Não conhece NAP').mean() * 100 if 'Jornada' in df.columns else 0

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
    st.metric("❌ Desconhecem", f"{pct_nao:.0f}%")

# ============================================================
# INTRODUÇÃO COMPLETA DO TRABALHO
# ============================================================
with st.expander("📖 INTRODUCAO COMPLETA DO TRABALHO", expanded=False):
    st.markdown("""
    # Introducao - Analise do NAP (Nucleo de Apoio Psicopedagogico)

    ## Objetivo da pesquisa

    Este dashboard apresenta os resultados de um questionario aplicado aos alunos para entender como eles enxergam o NAP.

    A pesquisa buscou identificar:
    - Quantos alunos conhecem, usaram ou desconhecem o servico
    - Quais sao as principais necessidades de apoio emocional e academico
    - Como os alunos percebem o suporte oferecido pela faculdade
    - O que impacta a intencao de usar o NAP

    ## Quais perguntas foram feitas?

    | Bloco | Pergunta | O que mede |
    |-------|----------|------------|
    | **Necessidade** | "Ja senti necessidade de apoio emocional durante a graduacao." | Se o aluno precisa de apoio |
    | **Conforto** | "Eu me sentiria confortavel em procurar ajuda dentro da instituicao." | Se ele se sente a vontade para pedir ajuda |
    | **Crenca** | "Acredito que servicos de apoio podem melhorar a experiencia academica." | Se ele acredita que funciona |
    | **Suporte** | "Eu sinto que ha suporte suficiente para dificuldades emocionais na faculdade." | Se ele percebe que a faculdade oferece apoio |
    | **Intencao** | "Eu ja pensei em utilizar o NAP em algum momento." | Se ele tem vontade de usar |
    | **Confianca** | "Tenho confianca na confidencialidade do atendimento do NAP." | Se ele confia no sigilo |

    ## Como dividimos os alunos?

    Com base na resposta a pergunta sobre o NAP, dividimos os alunos em 3 grupos:

    | Grupo | O que significa |
    |-------|-----------------|
    | **Nao conhece o NAP** | Nunca ouviu falar |
    | **Conhece mas nao usou** | Sabe que existe, mas nunca procurou |
    | **Usou o NAP** | Ja utilizou o servico |

    ## O que significam os numeros do dashboard

    | Numero | O que significa | O que e BOM? |
    |--------|-----------------|--------------|
    | **Total** | Quantos alunos responderam | - |
    | **Ja usaram** | Porcentagem que ja usou o NAP | Quanto maior, melhor |
    | **Necessidade** | O quanto os alunos PRECISAM de apoio (0 a 10) | Baixo (menos de 5) |
    | **Suporte** | O quanto eles PERCEBEM que a faculdade oferece apoio (0 a 10) | Alto (mais de 7) |
    | **Gap** | Diferenca entre necessidade e suporte | Negativo ou zero |
    | **Intencao** | O quanto gostariam de usar o NAP (0 a 10) | Alto (mais de 7) |
    | **Desconhecem** | Porcentagem que nunca ouviu falar | Baixo (menos de 20%) |

    ## Como calculamos o Gap?

    Gap = Necessidade - Suporte

    | Situacao | Resultado | Significado |
    |----------|-----------|-------------|
    | Precisa muito, nao percebe apoio | Gap positivo | PROBLEMA - Falta comunicacao |
    | Precisa pouco, percebe muito apoio | Gap negativo | IDEAL - Faculdade esta atendendo bem |
    | Precisa e percebe na mesma medida | Gap zero | OK - Equilibrado |

    ## O que e BOM?

    - Suporte alto (acima de 7)
    - Gap negativo
    - Intencao alta (acima de 7)
    - Poucos desconhecem o NAP (menos de 20%)

    ## O que e ALERTA?

    - Necessidade alta (acima de 7)
    - Suporte baixo (abaixo de 5)
    - Gap positivo (acima de 3)
    - Muitos desconhecem o NAP (mais de 40%)

    ## Como usar o dashboard

    1. Filtros na lateral esquerda
    2. Numeros no topo - visao geral
    3. Central de Alertas - problemas identificados
    4. Matriz de Correlacao - relacoes entre perguntas
    5. Graficos - comparacoes e evolucao

    ## Sobre privacidade

    - Todas as respostas foram anonimizadas
    - E-mails e dados pessoais foram removidos
    """)

# ============================================================
# AVISOS
# ============================================================
st.markdown("---")
st.subheader("⚠️ Central de Alertas")

col_a1, col_a2 = st.columns(2)

with col_a1:
    if gap > 3:
        st.error(f"🔴 **Gap Crítico:** {gap:.1f} pontos entre necessidade e suporte")
    elif gap < -1:
        st.success(f"🟢 **Gap positivo:** Suporte excede necessidade em {abs(gap):.1f} pontos")
    else:
        st.info(f"🟡 Gap controlado: {gap:.1f} pontos")

with col_a2:
    if pct_nao > 40:
        st.error(f"🔴 **Comunicação:** {pct_nao:.0f}% desconhecem o NAP")
    elif pct_nao > 20:
        st.warning(f"🟡 **Atenção:** {pct_nao:.0f}% desconhecem o NAP")
    else:
        st.success(f"🟢 {pct_nao:.0f}% desconhecem")

# ============================================================
# MATRIZ DE CORRELAÇÃO
# ============================================================
st.markdown("---")
st.subheader("📊 Matriz de Correlação")
st.caption("🔍 Valores próximos a 1 (vermelho) = perguntas sobem juntas. Valores próximos a -1 (azul) = relação inversa.")

# Bloco 1
bloco1_cols = [
    "Já senti necessidade de apoio emocional durante a graduação.",
    "Eu me sentiria confortável em procurar ajuda dentro da instituição.",
    "Eu sinto que há suporte suficiente para dificuldades emocionais na faculdade.",
    "Acredito que serviços de apoio podem melhorar a experiência acadêmica dos alunos."
]

nomes_curtos_bloco1 = {
    "Já senti necessidade de apoio emocional durante a graduação.": "Necessidade",
    "Eu me sentiria confortável em procurar ajuda dentro da instituição.": "Conforto",
    "Eu sinto que há suporte suficiente para dificuldades emocionais na faculdade.": "Suporte",
    "Acredito que serviços de apoio podem melhorar a experiência acadêmica dos alunos.": "Crença"
}

cols_exist_bloco1 = [col for col in bloco1_cols if col in df.columns]

if len(cols_exist_bloco1) >= 2:
    df_clean1 = df[cols_exist_bloco1].dropna()
    if len(df_clean1) >= 3:
        corr_matrix1 = df_clean1.corr()
        corr_matrix1 = corr_matrix1.rename(index=nomes_curtos_bloco1, columns=nomes_curtos_bloco1)
        mask1 = np.triu(np.ones_like(corr_matrix1, dtype=bool))
        corr_matrix_masked1 = corr_matrix1.mask(mask1)
        fig1 = px.imshow(corr_matrix_masked1, text_auto='.2f', aspect='auto', color_continuous_scale='RdBu_r', zmin=-1, zmax=1)
        fig1.update_layout(height=400)
        st.plotly_chart(fig1, use_container_width=True)
        st.caption(f"📊 Base: {len(df_clean1)} respostas completas")

st.info("ℹ️ As perguntas de diferentes blocos foram respondidas por grupos diferentes, por isso nao calculamos correlacao entre elas.")

# ============================================================
# FUNIL DE ADOÇÃO
# ============================================================
st.markdown("---")
st.subheader("📊 Funil de Adoção")
st.caption("🔍 Quantos alunos estao em cada etapa da jornada.")

if 'Jornada' in df.columns:
    funil = df['Jornada'].value_counts().reset_index()
    funil.columns = ['Status', 'Quantidade']
    ordem = ['Não conhece NAP', 'Conhece mas não usou', 'Usou NAP']
    funil['Status'] = pd.Categorical(funil['Status'], categories=ordem, ordered=True)
    funil = funil.sort_values('Status')
    fig = px.bar(funil, x='Status', y='Quantidade', color='Status', text='Quantidade')
    fig.update_layout(showlegend=False)
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
    fig_scores = px.bar(df_scores, x='Dimensão', y='Score', range_y=[0,10], text='Score', color='Dimensão')
    fig_scores.update_layout(showlegend=False)
    st.plotly_chart(fig_scores, use_container_width=True)

# ============================================================
# DISTRIBUIÇÕES DEMOGRÁFICAS
# ============================================================
st.markdown("---")
st.subheader("📈 Distribuições Demográficas")

col_d1, col_d2, col_d3 = st.columns(3)

with col_d1:
    if 'Faixa Etária' in df.columns:
        idade = df['Faixa Etária'].value_counts().reset_index()
        idade.columns = ['Faixa Etária', 'Quantidade']
        fig = px.pie(idade, values='Quantidade', names='Faixa Etária', title="Faixa Etária")
        st.plotly_chart(fig, use_container_width=True)

with col_d2:
    if 'Gênero' in df.columns:
        genero = df['Gênero'].value_counts().reset_index()
        genero.columns = ['Gênero', 'Quantidade']
        fig = px.pie(genero, values='Quantidade', names='Gênero', title="Gênero")
        st.plotly_chart(fig, use_container_width=True)

with col_d3:
    if 'Período' in df.columns:
        periodo = df['Período'].value_counts().reset_index()
        periodo.columns = ['Período', 'Quantidade']
        fig = px.pie(periodo, values='Quantidade', names='Período', title="Período")
        st.plotly_chart(fig, use_container_width=True)

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.success("✅ Dashboard completo com legendas explicativas!")

with st.expander("📋 Resumo Executivo para Gestão"):
    st.markdown(f"""
    ### Principais conclusoes:
    
    1. **Comunicacao e a prioridade maxima:** {int(pct_nao)}% dos alunos desconhecem o NAP.
    2. **Gap de {gap:.1f} pontos:** Alunos precisam de apoio ({necessidade:.1f}/10) mas nao percebem que a faculdade oferece ({suporte:.1f}/10).
    3. **Quem usa, aprova:** As avaliacoes dos usuarios sao positivas.
    
    ### Recomendacoes:
    
    - Campanha de divulgacao imediata
    - Comunicar claramente os servicos oferecidos
    - Coletar e divulgar depoimentos de alunos que usaram
    - Acompanhar evolucao do gap semestralmente
    """)

st.caption(f"📊 Dashboard atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | Base: {len(df)} alunos")
