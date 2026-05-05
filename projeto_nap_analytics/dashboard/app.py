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
# Depois de df = carregar_e_processar(), adicione:

# ============================================================
# DEBUG - MOSTRAR COLUNAS REAIS (REMOVER DEPOIS)
# ============================================================
with st.expander("🔧 DEBUG - Colunas encontradas no CSV"):
    st.write("**Colunas relacionadas ao NAP:**")
    for col in df.columns:
        if any(word in col.lower() for word in ['nap', 'emocional', 'confort', 'suporte', 'crença', 'acredito', 'confiança', 'confidencial', 'acessar']):
            st.write(f"- `{col}`")
    
    st.write("**Primeiras 5 linhas de dados:**")
    st.dataframe(df.head())

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
# HEATMAP COM LEGENDA (COM MÁSCARA NO TRIÂNGULO SUPERIOR)
# ============================================================
st.markdown("---")
st.subheader("📊 Matriz de Correlação")
st.caption("🔍 **O que significa?** Valores próximos a 1 (vermelho) indicam que as perguntas tendem a subir juntas. Valores próximos a -1 (azul) indicam relação inversa. Quanto mais forte a cor, mais forte a relação.")

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
    
    # Máscara para mostrar apenas o triângulo inferior
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    corr_matrix_masked = corr_matrix.mask(mask)
    
    fig_corr = px.imshow(
        corr_matrix_masked, 
        text_auto='.2f', 
        aspect='auto', 
        color_continuous_scale='RdBu_r', 
        zmin=-1, 
        zmax=1
    )
    fig_corr.update_layout(height=500)
    st.plotly_chart(fig_corr, use_container_width=True)
    
    with st.expander("📖 Como interpretar este gráfico"):
        st.markdown("""
        - **Vermelho forte (> 0.7)**: Perguntas fortemente relacionadas. Ex: quem sente necessidade também tende a ter intenção de usar.
        - **Azul forte (< -0.7)**: Relação inversa. Ex: quem tem muito preconceito pode ter menos intenção (se aplicável).
        - **Próximo de zero**: Sem relação significativa.
        - **Valores em branco**: Triângulo superior omitido para evitar repetição (matriz é simétrica).
        """)

# ============================================================
# COMPARAÇÃO CAMPI COM LEGENDA
# ============================================================
st.markdown("---")
st.subheader("🏢 Comparação entre Campi")
st.caption("🔍 **O que mostra?** Compara Necessidade, Suporte e Intenção entre os campi. Quanto maior a barra, melhor o índice.")

if 'Campus' in df.columns and len(df['Campus'].unique()) > 1:
    campi = df.groupby('Campus').agg({
        'score_necessidade': 'mean',
        'score_suporte': 'mean',
        'score_intencao': 'mean'
    }).reset_index()
    campi.columns = ['Campus', 'Necessidade', 'Suporte', 'Intenção']
    
    fig_campi = go.Figure()
    fig_campi.add_trace(go.Bar(name='Necessidade', x=campi['Campus'], y=campi['Necessidade'], text=campi['Necessidade'].round(1), textposition='auto', marker_color='#e74c3c'))
    fig_campi.add_trace(go.Bar(name='Suporte', x=campi['Campus'], y=campi['Suporte'], text=campi['Suporte'].round(1), textposition='auto', marker_color='#3498db'))
    fig_campi.add_trace(go.Bar(name='Intenção', x=campi['Campus'], y=campi['Intenção'], text=campi['Intenção'].round(1), textposition='auto', marker_color='#2ecc71'))
    fig_campi.update_layout(barmode='group', yaxis_range=[0, 10])
    st.plotly_chart(fig_campi, use_container_width=True)
    
    with st.expander("📖 Como interpretar este gráfico"):
        st.markdown("""
        - **Necessidade (vermelho)**: Quanto maior, mais os alunos sentem falta de apoio.
        - **Suporte (azul)**: Quanto maior, melhor os alunos percebem o suporte da faculdade.
        - **Intenção (verde)**: Quanto maior, mais dispostos a usar o NAP.
        - **Ideal**: Suporte e Intenção altos, Necessidade equilibrada.
        """)

# ============================================================
# ANÁLISE DE QUALIDADE DO SERVIÇO (QUEM USOU O NAP)
# ============================================================
st.markdown("---")
st.subheader("⭐ Análise da Qualidade do Serviço (Quem usou o NAP)")

# Filtrar quem usou o NAP
df_usou = df[df['Jornada'] == 'Usou NAP']

if len(df_usou) >= 5:
    st.caption("🔍 **Base:** Alunos que utilizaram o NAP")
    
    # 1. Avaliação média
    st.markdown("### 📊 Avaliação dos Usuários")
    
    col_q1, col_q2, col_q3 = st.columns(3)
    
    with col_q1:
        if 'O atendimento do NAP atendeu às minhas expectativas.' in df_usou.columns:
            nota = df_usou['O atendimento do NAP atendeu às minhas expectativas.'].mean()
            st.metric("🎯 Atendeu expectativas", f"{nota:.1f}/10")
    
    with col_q2:
        if 'Eu recomendaria o NAP para outros estudantes.' in df_usou.columns:
            nota = df_usou['Eu recomendaria o NAP para outros estudantes.'].mean()
            st.metric("👍 Recomendaria", f"{nota:.1f}/10")
    
    with col_q3:
        if 'Confio no profissionalismo do atendimento oferecido pelo NAP.' in df_usou.columns:
            nota = df_usou['Confio no profissionalismo do atendimento oferecido pelo NAP.'].mean()
            st.metric("🔒 Confiança no profissionalismo", f"{nota:.1f}/10")
    
    # 2. Gráfico de radar
    st.markdown("### 📈 Perfil de Satisfação")
    
    perguntas_qualidade = [
        "O atendimento do NAP atendeu às minhas expectativas.",
        "Senti que fui ouvido(a) e compreendido(a) no atendimento.",
        "Confio no profissionalismo do atendimento oferecido pelo NAP.",
        "O NAP contribuiu para o meu bem-estar emocional.",
        "Eu recomendaria o NAP para outros estudantes."
    ]
    
    perguntas_existentes = [p for p in perguntas_qualidade if p in df_usou.columns]
    
    if perguntas_existentes:
        medias = [df_usou[p].mean() for p in perguntas_existentes]
        nomes_curtos_q = [
            "Atendeu expectativas",
            "Foi ouvido",
            "Confiança",
            "Bem-estar",
            "Recomendaria"
        ][:len(perguntas_existentes)]
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=medias,
            theta=nomes_curtos_q,
            fill='toself',
            name='Usuários do NAP',
            line_color='#3498db'
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
            showlegend=True,
            title="Perfil de Satisfação (média)"
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        
        st.info("💡 **Interpretação:** Usuários aprovam o serviço. O desafio é aumentar a adesão e coletar mais depoimentos.")
    
    # 3. Depoimentos
    st.markdown("### 💬 Depoimentos dos usuários")
    st.info("📝 Invista em coletar e divulgar depoimentos de alunos que usaram o NAP para incentivar novos usuários.")

elif len(df_usou) >= 2:
    st.warning(f"📊 Amostra pequena ({len(df_usou)} usuários). Os dados abaixo são apenas indicativos.")
    
    # Mostra apenas métricas básicas, sem radar
    if 'O atendimento do NAP atendeu às minhas expectativas.' in df_usou.columns:
        nota = df_usou['O atendimento do NAP atendeu às minhas expectativas.'].mean()
        st.metric("🎯 Atendeu expectativas (amostra pequena)", f"{nota:.1f}/10")
    
    if 'Eu recomendaria o NAP para outros estudantes.' in df_usou.columns:
        nota = df_usou['Eu recomendaria o NAP para outros estudantes.'].mean()
        st.metric("👍 Recomendaria (amostra pequena)", f"{nota:.1f}/10")

else:
    st.info("📊 Poucos dados para análise da qualidade do serviço. Aumente a amostra para análises robustas.")
    st.markdown("""
    **Sugestões para melhorar:**
    - Incentivar mais alunos a usar o NAP
    - Coletar feedback qualitativo (entrevistas)
    - Acompanhar a evolução da satisfação
    """)

# ============================================================
# EVOLUÇÃO POR SEMESTRE
# ============================================================
st.markdown("---")
st.subheader("📚 Evolução por Semestre")
st.caption("🔍 **O que mostra?** Como a Necessidade, Suporte e Intenção mudam ao longo dos semestres. Idealmente, o Suporte deveria aumentar ou se manter estável.")

if 'Semestre' in df.columns:
    df['Semestre_Num'] = df['Semestre'].str.extract(r'(\d+)').astype(float)
    evolucao = df.groupby('Semestre_Num').agg({
        'score_necessidade': 'mean',
        'score_suporte': 'mean',
        'score_intencao': 'mean'
    }).reset_index().dropna()
    evolucao = evolucao.sort_values('Semestre_Num')  # Garante ordenação correta
    
    if len(evolucao) >= 2:
        fig_evo = go.Figure()
        fig_evo.add_trace(go.Scatter(x=evolucao['Semestre_Num'], y=evolucao['score_necessidade'], mode='lines+markers', name='Necessidade', line=dict(color='#e74c3c', width=3)))
        fig_evo.add_trace(go.Scatter(x=evolucao['Semestre_Num'], y=evolucao['score_suporte'], mode='lines+markers', name='Suporte', line=dict(color='#3498db', width=3)))
        fig_evo.add_trace(go.Scatter(x=evolucao['Semestre_Num'], y=evolucao['score_intencao'], mode='lines+markers', name='Intenção', line=dict(color='#2ecc71', width=3)))
        fig_evo.update_layout(yaxis_range=[0, 10], xaxis_title="Semestre", yaxis_title="Score (0-10)")
        st.plotly_chart(fig_evo, use_container_width=True)
        
        with st.expander("📖 Como interpretar este gráfico"):
            st.markdown("""
            - **Necessidade (vermelho)**: Deveria diminuir ao longo do tempo (alunos se adaptam)
            - **Suporte (azul)**: Deveria aumentar (faculdade melhora acolhimento)
            - **Intenção (verde)**: Deveria aumentar (mais conhecimento sobre o NAP)
            - **Queda no suporte** é um alerta para a coordenação
            """)
        
        primeiro_sup = evolucao.iloc[0]['score_suporte']
        ultimo_sup = evolucao.iloc[-1]['score_suporte']
        if ultimo_sup < primeiro_sup:
            st.warning(f"📉 O suporte percebido caiu {primeiro_sup - ultimo_sup:.1f} pontos ao longo dos semestres")
    else:
        st.info("Dados insuficientes para análise de evolução por semestre")

# ============================================================
# SCORES POR DIMENSÃO
# ============================================================
st.markdown("---")
st.subheader("📊 Scores por Dimensão")
st.caption("🔍 **O que mostra?** Avaliação do NAP em três dimensões: Necessidade (o quanto o aluno precisa), Suporte (o quanto a faculdade oferece) e Intenção (disposição para usar).")

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
    
    with st.expander("📖 Como interpretar este gráfico"):
        st.markdown("""
        - **Necessidade alta (> 7)**: Alunos reconhecem que precisam de apoio
        - **Suporte baixo (< 5)**: Alunos não percebem que a faculdade oferece apoio
        - **Gap (diferença)**: Quanto maior, pior. Indica desalinhamento entre necessidade e oferta
        - **Gap negativo**: Suporte excede a necessidade (situação ideal)
        """)

# ============================================================
# PRIORIZAÇÃO
# ============================================================
st.markdown("---")
st.subheader("🎯 Priorização de Problemas")
st.caption("🔍 **O que mostra?** Prioridade = Impacto / Esforço. Quanto maior a barra, mais urgente é resolver o problema.")

problemas = []

col_info = None
for col in df.columns:
    if 'sei a quem recorrer' in col.lower():
        col_info = col
        break

if col_info:
    dados = pd.to_numeric(df[col_info], errors='coerce').dropna()
    if len(dados) > 0:
        impacto_info = 10 - dados.mean()  # Quanto menos sabe, maior o impacto
        problemas.append({"Problema": "Falta de informação", "Impacto": impacto_info, "Esforço": 2})

col_prec = None
for col in df.columns:
    if 'preconceito' in col.lower():
        col_prec = col
        break

if col_prec:
    dados = pd.to_numeric(df[col_prec], errors='coerce').dropna()
    if len(dados) > 0:
        impacto_prec = dados.mean()  # Quanto mais preconceito, maior o impacto
        problemas.append({"Problema": "Preconceito", "Impacto": impacto_prec, "Esforço": 6})

if gap > 3:
    problemas.append({"Problema": f"Gap de {gap:.1f} pontos", "Impacto": gap, "Esforço": 5})

if problemas:
    df_problemas = pd.DataFrame(problemas)
    df_problemas['Prioridade'] = df_problemas['Impacto'] / df_problemas['Esforço']
    df_problemas = df_problemas.sort_values('Prioridade', ascending=False)
    
    fig_prior = px.bar(df_problemas, x='Problema', y='Prioridade', color='Problema', text=df_problemas['Prioridade'].round(2))
    st.plotly_chart(fig_prior, use_container_width=True)
    
    with st.expander("📖 Como interpretar este gráfico"):
        st.markdown("""
        - **Prioridade mais alta** = maior relação Impacto/Esforço
        - **Falta de informação** tem alto impacto e baixo esforço → PRIORIDADE MÁXIMA
        - **Preconceito** tem esforço alto (mudança cultural demora)
        - **Gap** é um problema estrutural que exige ação coordenada
        """)

# ============================================================
# FUNIL
# ============================================================
st.markdown("---")
st.subheader("📊 Funil de Adoção")
st.caption("🔍 **O que mostra?** Quantos alunos estão em cada etapa: desconhecem → conhecem mas não usam → usam.")

if 'Jornada' in df.columns:
    funil = df['Jornada'].value_counts().reset_index()
    funil.columns = ['Status', 'Quantidade']
    
    # Ordem lógica do funil
    ordem = ['Não conhece NAP', 'Conhece mas não usou', 'Usou NAP']
    funil['Status'] = pd.Categorical(funil['Status'], categories=ordem, ordered=True)
    funil = funil.sort_values('Status')
    
    fig = px.bar(funil, x='Status', y='Quantidade', color='Status', text='Quantidade')
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("📖 Como interpretar este gráfico"):
        st.markdown("""
        - **Desconhecem**: Alvos da campanha de divulgação
        - **Conhecem mas não usam**: Barreira de ativação (falta de confiança, preconceito, etc.)
        - **Usam**: O objetivo final. Poucos atingem essa etapa.
        """)

# ============================================================
# DISTRIBUIÇÕES DEMOGRÁFICAS
# ============================================================
st.markdown("---")
st.subheader("📈 Distribuições Demográficas")
st.caption("🔍 **O que mostra?** Perfil dos respondentes por idade, gênero e período.")

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
# DISTRIBUIÇÃO POR CAMPUS
# ============================================================
st.markdown("---")
if 'Campus' in df.columns:
    st.subheader("🏢 Distribuição por Campus")
    st.caption("🔍 **O que mostra?** Quantidade de respondentes por campus.")
    campus = df['Campus'].value_counts().reset_index()
    campus.columns = ['Campus', 'Quantidade']
    fig = px.bar(campus, x='Campus', y='Quantidade', color='Campus', text='Quantidade')
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# FOOTER E RESUMO EXECUTIVO
# ============================================================
st.markdown("---")
st.success("✅ Dashboard completo com legendas explicativas!")

# Resumo executivo
with st.expander("📋 Resumo Executivo para Gestão"):
    st.markdown(f"""
    ### Principais conclusões:
    
    1. **Comunicação é a prioridade máxima:** {pct_nao:.0f}% dos alunos desconhecem o NAP.
    2. **Gap de {gap:.1f} pontos:** Alunos precisam de apoio ({necessidade:.1f}/10) mas não percebem que a faculdade oferece ({suporte:.1f}/10).
    3. **Quem usa, aprova:** As avaliações dos usuários são positivas.
    
    ### Recomendações:
    
    - ✅ Campanha de divulgação imediata
    - ✅ Comunicar claramente os serviços oferecidos
    - ✅ Coletar e divulgar depoimentos de alunos que usaram
    - ✅ Acompanhar evolução do gap semestralmente
    """)

st.caption(f"📊 Dashboard atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | Base: {len(df)} alunos")
