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

# ============================================================
# INTRODUCAO - LOGICA, GRUPOS E PERGUNTAS
# ============================================================

with st.expander("INTRODUCAO - Como ler este dashboard", expanded=True):
    st.markdown("""
    ### O que estamos medindo?

    | Indicador | O que significa | Ideal |
    |-----------|-----------------|-------|
    | Necessidade | Alunos que sentem falta de apoio emocional/academico | Baixo |
    | Crenca | Alunos que acreditam que servicos de apoio ajudam | Alto |
    | Suporte | Alunos que percebem que a faculdade oferece apoio | Alto |
    | Gap | Diferenca entre necessidade e suporte | Negativo ou zero |
    | Intencao | Alunos dispostos a usar o NAP | Alto |

    ---

    ### Os 3 grupos de alunos (Jornada)

    | Grupo | O que significa |
    |-------|-----------------|
    | Nao conhece o NAP | Alvos da campanha de divulgacao |
    | Conhece mas nao usou | Barreira de ativacao |
    | Usou o NAP | Avaliam a qualidade do servico |

    ---

    ### Como interpretar o Gap

    Gap = Necessidade - Suporte

    | Resultado | Significado |
    |-----------|-------------|
    | Gap positivo (+) | Alunos precisam mais do que percebem -> FALTA DE COMUNICACAO |
    | Gap negativo (-) | Suporte excede necessidade -> SITUACAO IDEAL |
    | Gap proximo de zero | Necessidade e suporte estao alinhados |

    ---

    ### Como usar
    1. Filtros na lateral esquerda
    2. KPIs coloridos
    3. Alertas automaticos
    4. Correlacoes
    5. Funil de adocao
    """)

st.markdown("---")

@st.cache_data
def carregar_e_processar():
    df = carregar_dados_brutos()
    df = aplicar_jornada(df)
    df = calcular_scores(df)
    df = limpar_colunas(df)
    return df

df = carregar_e_processar()

# ============================================================
# VERIFICACAO DE DADOS
# ============================================================
if df.empty:
    st.error("Nao foi possivel carregar os dados. Verifique o arquivo dados.csv")
    st.stop()

# ============================================================
# FUNCAO PARA GERAR HTML (RELATORIO)
# ============================================================
def gerar_html_relatorio(df):
    necessidade = df['score_necessidade'].mean() if 'score_necessidade' in df.columns else 0
    suporte = df['score_suporte'].mean() if 'score_suporte' in df.columns else 0
    gap = df['score_gap'].mean() if 'score_gap' in df.columns else 0
    pct_usou = (df['Jornada'] == 'Usou NAP').mean() * 100 if 'Jornada' in df.columns else 0
    
    html = "<html><body>"
    html += "<h1>NAP - Relatorio Executivo</h1>"
    html += f"<p>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>"
    html += f"<p>Total: {len(df)} alunos</p>"
    html += f"<p>Usaram o NAP: {int(pct_usou)}%</p>"
    html += f"<p>Necessidade: {necessidade:.1f}/10</p>"
    html += f"<p>Suporte: {suporte:.1f}/10</p>"
    html += f"<p>Gap: {gap:.1f}</p>"
    html += "</body></html>"
    return html

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.title("Filtros")
st.sidebar.markdown("---")

if 'Campus' in df.columns:
    campus_opcoes = ['Todos'] + sorted(df['Campus'].dropna().unique().tolist())
    campus_selecionado = st.sidebar.selectbox("Campus", campus_opcoes)
    if campus_selecionado != 'Todos':
        df = df[df['Campus'] == campus_selecionado]

if 'Periodo' in df.columns:
    periodo_opcoes = ['Todos'] + sorted(df['Periodo'].dropna().unique().tolist())
    periodo_selecionado = st.sidebar.selectbox("Periodo", periodo_opcoes)
    if periodo_selecionado != 'Todos':
        df = df[df['Periodo'] == periodo_selecionado]

if 'Faixa Etaria' in df.columns:
    idade_opcoes = ['Todas'] + sorted(df['Faixa Etaria'].dropna().unique().tolist())
    idade_selecionada = st.sidebar.selectbox("Faixa Etaria", idade_opcoes)
    if idade_selecionada != 'Todas':
        df = df[df['Faixa Etaria'] == idade_selecionada]

if 'Genero' in df.columns:
    generos = df['Genero'].dropna().unique().tolist()
    genero_opcoes = ['Todos'] + sorted(generos)
    genero_selecionado = st.sidebar.selectbox("Genero", genero_opcoes)
    if genero_selecionado != 'Todos':
        df = df[df['Genero'] == genero_selecionado]

if 'Semestre' in df.columns:
    semestre_opcoes = ['Todos'] + sorted(df['Semestre'].dropna().unique().tolist())
    semestre_selecionado = st.sidebar.selectbox("Semestre", semestre_opcoes)
    if semestre_selecionado != 'Todos':
        df = df[df['Semestre'] == semestre_selecionado]

if 'Jornada' in df.columns:
    status_opcoes = ['Todos'] + sorted(df['Jornada'].dropna().unique().tolist())
    status_selecionado = st.sidebar.selectbox("Status no NAP", status_opcoes)
    if status_selecionado != 'Todos':
        df = df[df['Jornada'] == status_selecionado]

st.sidebar.markdown("---")

# Exportar Relatorio HTML
html_report = gerar_html_relatorio(df)
b64 = base64.b64encode(html_report.encode()).decode()
href = f'<a href="data:text/html;base64,{b64}" download="relatorio_nap.html" style="text-decoration: none;"><button style="background-color: #e74c3c; color: white; padding: 10px; border: none; border-radius: 5px; cursor: pointer; width: 100%;">Relatorio</button></a>'
st.sidebar.markdown(href, unsafe_allow_html=True)

# Exportar CSV
csv = df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="Baixar dados (CSV)",
    data=csv,
    file_name=f"nap_dados_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
    mime="text/csv",
)

st.sidebar.caption(f"{len(df)} registros")

# ============================================================
# DASHBOARD
# ============================================================
st.title("NAP - Núcleo de Apoio Psicopedagogico")
st.markdown("### Painel de Jornada e Experiencia do Aluno")
st.markdown("---")

# ============================================================
# KPIs
# ============================================================
st.subheader("Visao Geral")

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
    st.metric("Total", len(df))
with col2:
    st.metric("Ja usaram", f"{pct_usou:.0f}%")
with col3:
    st.metric("Necessidade", f"{necessidade:.1f}/10")
with col4:
    st.metric("Suporte", f"{suporte:.1f}/10")
with col5:
    st.metric("Gap", f"{gap:.1f}")
with col6:
    st.metric("Intencao", f"{intencao:.1f}/10")
with col7:
    st.metric("Conhecem", f"{pct_conhece:.0f}%")
with col8:
    st.metric("Desconhecem", f"{pct_nao:.0f}%")

# ============================================================
# AVISOS
# ============================================================
st.markdown("---")
st.subheader("Central de Alertas")

col_a1, col_a2 = st.columns(2)

with col_a1:
    if gap > 3:
        st.error(f"Gap Critico: {gap:.1f} pontos entre necessidade e suporte")
    elif gap < -1:
        st.success(f"Gap positivo: Suporte excede necessidade em {abs(gap):.1f} pontos")
    else:
        st.info(f"Gap controlado: {gap:.1f} pontos")

with col_a2:
    if pct_nao > 40:
        st.error(f"Comunicacao: {pct_nao:.0f}% desconhecem o NAP")
    elif pct_nao > 20:
        st.warning(f"Atencao: {pct_nao:.0f}% desconhecem o NAP")
    else:
        st.success(f"{pct_nao:.0f}% desconhecem")

# ============================================================
# MATRIZ DE CORRELACAO
# ============================================================
st.markdown("---")
st.subheader("Matriz de Correlacao")
st.caption("Valores proximos a 1 = perguntas sobem juntas. Valores proximos a -1 = relacao inversa.")

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
    "Acredito que serviços de apoio podem melhorar a experiência acadêmica dos alunos.": "Crenca"
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
        st.caption(f"Base: {len(df_clean1)} respostas completas")

# ============================================================
# FUNIL DE ADOCAO
# ============================================================
st.markdown("---")
st.subheader("Funil de Adocao")

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
# SCORES POR DIMENSAO
# ============================================================
st.markdown("---")
st.subheader("Scores por Dimensao")

scores_data = []
if necessidade > 0:
    scores_data.append({"Dimensao": "Necessidade", "Score": necessidade})
if suporte > 0:
    scores_data.append({"Dimensao": "Suporte", "Score": suporte})
if intencao > 0:
    scores_data.append({"Dimensao": "Intencao", "Score": intencao})

if scores_data:
    df_scores = pd.DataFrame(scores_data)
    fig_scores = px.bar(df_scores, x='Dimensao', y='Score', range_y=[0,10], text='Score', color='Dimensao')
    fig_scores.update_layout(showlegend=False)
    st.plotly_chart(fig_scores, use_container_width=True)

# ============================================================
# DISTRIBUICOES DEMOGRAFICAS
# ============================================================
st.markdown("---")
st.subheader("Distribuicoes Demograficas")

col_d1, col_d2, col_d3 = st.columns(3)

with col_d1:
    if 'Faixa Etária' in df.columns:
        idade = df['Faixa Etária'].value_counts().reset_index()
        idade.columns = ['Faixa Etaria', 'Quantidade']
        fig = px.pie(idade, values='Quantidade', names='Faixa Etaria', title="Faixa Etaria")
        st.plotly_chart(fig, use_container_width=True)

with col_d2:
    if 'Gênero' in df.columns:
        genero = df['Gênero'].value_counts().reset_index()
        genero.columns = ['Genero', 'Quantidade']
        fig = px.pie(genero, values='Quantidade', names='Genero', title="Genero")
        st.plotly_chart(fig, use_container_width=True)

with col_d3:
    if 'Período' in df.columns:
        periodo = df['Período'].value_counts().reset_index()
        periodo.columns = ['Periodo', 'Quantidade']
        fig = px.pie(periodo, values='Quantidade', names='Periodo', title="Periodo")
        st.plotly_chart(fig, use_container_width=True)

# ============================================================
# RESULTADOS FINAIS
# ============================================================
st.markdown("---")
st.success("Dashboard completo!")

with st.expander("Resumo Executivo para Gestao"):
    st.markdown("### Principais conclusoes:\n\n")
    st.markdown(f"1. Comunicacao e a prioridade maxima: {int(pct_nao)}% dos alunos desconhecem o NAP.")
    st.markdown(f"2. Gap de {gap:.1f} pontos: Alunos precisam de apoio ({necessidade:.1f}/10) mas nao percebem que a faculdade oferece ({suporte:.1f}/10).")
    st.markdown("3. Quem usa, aprova: As avaliacoes dos usuarios sao positivas.\n\n")
    st.markdown("### Recomendacoes:\n")
    st.markdown("- Campanha de divulgacao imediata")
    st.markdown("- Comunicar claramente os servicos oferecidos")
    st.markdown("- Coletar e divulgar depoimentos de alunos que usaram")
    st.markdown("- Acompanhar evolucao do gap semestralmente")

st.caption(f"Dashboard atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | Base: {len(df)} alunos")
