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
# INTRODUÇÃO COMPLETA DO TRABALHO (ADICIONADA)
# ============================================================
with st.expander("📖 **INTRODUÇÃO COMPLETA DO TRABALHO**", expanded=False):
    st.markdown("""
    # Introducao - Analise do NAP (Nucleo de Apoio Psicopedagogico)

    ## Objetivo da pesquisa

    Este dashboard apresenta os resultados de um questionario aplicado aos alunos para entender como eles enxergam o NAP.

    A pesquisa buscou identificar:
    - Quantos alunos conhecem, usaram ou desconhecem o servico
    - Quais sao as principais necessidades de apoio emocional e academico
    - Como os alunos percebem o suporte oferecido pela faculdade
    - O que impacta a intencao de usar o NAP

    ---

    ## Quais perguntas foram feitas?

    | Bloco | Pergunta | O que mede |
    |-------|----------|------------|
    | **Necessidade** | "Ja senti necessidade de apoio emocional durante a graduacao." | Se o aluno precisa de apoio |
    | **Conforto** | "Eu me sentiria confortavel em procurar ajuda dentro da instituicao." | Se ele se sente a vontade para pedir ajuda |
    | **Crenca** | "Acredito que servicos de apoio podem melhorar a experiencia academica." | Se ele acredita que funciona |
    | **Suporte** | "Eu sinto que ha suporte suficiente para dificuldades emocionais na faculdade." | Se ele percebe que a faculdade oferece apoio |
    | **Intencao** | "Eu ja pensei em utilizar o NAP em algum momento." | Se ele tem vontade de usar |
    | **Confianca** | "Tenho confianca na confidencialidade do atendimento do NAP." | Se ele confia no sigilo |

    ---

    ## Onde cada pergunta aparece no dashboard?

    | Pergunta | Aparece nos KPIs? | Aparece na Matriz de Correlacao? |
    |----------|-------------------|----------------------------------|
    | "Ja senti necessidade de apoio emocional..." | Sim (como Necessidade) | Sim (Bloco 1) |
    | "Eu me sentiria confortavel em procurar ajuda..." | Nao | Sim (Bloco 1) |
    | "Acredito que servicos de apoio podem melhorar..." | Nao | Sim (Bloco 1) |
    | "Eu sinto que ha suporte suficiente..." | Sim (como Suporte) | Sim (Bloco 1) |
    | "Eu ja pensei em utilizar o NAP..." | Sim (como Intencao) | Sim (Bloco 2) |
    | "Tenho confianca na confidencialidade..." | Nao | Sim (Bloco 2) |

    > **Por que Conforto e Crenca nao aparecem nos KPIs?**  
    > Porque eles sao perguntas de apoio que compoem o score_necessidade. Eles aparecem APENAS na Matriz de Correlacao.

    ---

    ## Como os scores foram calculados?

    Cada resposta vai de **0 a 10**. Os scores sao **medias** das perguntas de cada bloco:

    | Score | Perguntas que compoem | Formula |
    |-------|----------------------|---------|
    | **score_necessidade** | Necessidade + Conforto | (Necessidade + Conforto) / 2 |
    | **score_suporte** | Suporte | Valor unico da pergunta |
    | **score_intencao** | Intencao + Confianca | (Intencao + Confianca) / 2 |
    | **score_gap** | Diferenca entre necessidade e suporte | score_necessidade - score_suporte |

    **Exemplo pratico:** Se um aluno respondeu:
    - Necessidade = 8
    - Conforto = 6
    - Suporte = 4
    - Intencao = 7
    - Confianca = 9

    Seus scores individuais seriam:
    - score_necessidade = (8 + 6) / 2 = 7
    - score_suporte = 4
    - score_gap = 7 - 4 = 3
    - score_intencao = (7 + 9) / 2 = 8

    **Os numeros que voce ve no dashboard sao as MEDIAS desses scores para TODOS os alunos.**

    ---

    ## O que a Matriz de Correlacao mostra?

    A matriz mostra como as perguntas se relacionam dentro de cada bloco.

    **Bloco 1 (Necessidade, Conforto, Suporte, Crenca):**

    | Correlacao | Se for positiva | Se for negativa |
    |------------|-----------------|-----------------|
    | **Necessidade ↔ Suporte** | Quem precisa percebe que tem apoio | Quem mais precisa, menos percebe apoio (ALERTA) |
    | **Conforto ↔ Crenca** | Quem se sente confortavel acredita mais no servico (BOM SINAL) | - |
    | **Necessidade ↔ Conforto** | Quem precisa se sente confortavel para pedir ajuda | Quem precisa tem vergonha/receio |

    **Bloco 2 (Intencao, Confianca):**

    | Correlacao | Significado |
    |------------|-------------|
    | **Intencao ↔ Confianca** | Quem confia no sigilo tem mais intencao de usar o NAP |

    ---

    ## Como dividimos os alunos?

    Com base na resposta a pergunta sobre o NAP, dividimos os alunos em 3 grupos:

    | Grupo | O que significa |
    |-------|-----------------|
    | **Nao conhece o NAP** | Nunca ouviu falar |
    | **Conhece mas nao usou** | Sabe que existe, mas nunca procurou |
    | **Usou o NAP** | Ja utilizou o servico |

    ---

    ## O que significam os numeros do dashboard

    | Numero | Como e calculado | O que significa | O que e BOM? |
    |--------|------------------|-----------------|--------------|
    | **Total** | Contagem de respostas | Quantos alunos responderam | - |
    | **Ja usaram** | (Usaram NAP / Total) * 100 | Porcentagem que ja usou o NAP | Quanto maior, melhor |
    | **Necessidade** | Media do score_necessidade | O quanto os alunos PRECISAM de apoio (0 a 10) | Baixo (menos de 5) |
    | **Suporte** | Media do score_suporte | O quanto eles PERCEBEM que a faculdade oferece apoio (0 a 10) | Alto (mais de 7) |
    | **Gap** | Necessidade - Suporte | Diferenca entre necessidade e suporte | Negativo ou zero |
    | **Intencao** | Media do score_intencao | O quanto gostariam de usar o NAP (0 a 10) | Alto (mais de 7) |
    | **Conhecem** | (Conhece mas nao usou / Total) * 100 | Porcentagem que conhece mas nao usou | - |
    | **Desconhecem** | (Nao conhece / Total) * 100 | Porcentagem que nunca ouviu falar | Baixo (menos de 20%) |

    ---

    ## Como interpretar o Gap?

    | Situacao | Calculo | Resultado | Significado |
    |----------|---------|-----------|-------------|
    | Precisa muito, nao percebe apoio | 8 - 3 = | Gap +5 | PROBLEMA - Falta comunicacao |
    | Precisa pouco, percebe muito apoio | 3 - 8 = | Gap -5 | IDEAL - Faculdade esta atendendo bem |
    | Precisa e percebe na mesma medida | 6 - 6 = | Gap 0 | OK - Equilibrado |

    ---

    ## O que e BOM e o que e ALERTA?

    | Indicador | BOM (Verde) | ALERTA (Vermelho) |
    |-----------|-------------|-------------------|
    | **Necessidade** | Abaixo de 5 | Acima de 7 |
    | **Suporte** | Acima de 7 | Abaixo de 5 |
    | **Gap** | Negativo ou zero | Acima de 3 |
    | **Intencao** | Acima de 7 | Abaixo de 5 |
    | **Desconhecem** | Abaixo de 20% | Acima de 40% |

    ---

    ## Como usar o dashboard

    1. **Filtros na lateral esquerda** -> Selecione campus, periodo, genero, semestre
    2. **Numeros no topo** -> Visao geral dos indicadores (atualizam com filtros)
    3. **Central de Alertas** -> Problemas identificados automaticamente
    4. **Matriz de Correlacao** -> Mostra como as perguntas se relacionam dentro de cada bloco
    5. **Funil de Adocao** -> Quantos alunos em cada etapa da jornada
    6. **Analise de Qualidade** -> Avaliacao de quem USOU o NAP (atendimento, recomendacao)
    7. **Graficos** -> Comparacoes entre campi, evolucao por semestre, perfil dos alunos

    ---

    ## Sobre os dados e privacidade

    - **Fluxo condicional do Forms:** Quem respondeu um bloco nao respondeu os outros. Por isso algumas perguntas tem menos respostas.
    - **Medias calculadas apenas com quem respondeu:** Os campos vazios sao ignorados automaticamente.
    - **Dados anonimizados:** E-mails e dados pessoais foram removidos.
    - **Ninguem consegue identificar quem respondeu o que.**

    ---

    ## Resumo rapido para consulta

    | Se voce quer saber... | Olhe para... | O que e bom... |
    |-----------------------|---------------|----------------|
    | Se os alunos precisam de apoio | **Necessidade** | Numero baixo (< 5) |
    | Se eles percebem que a faculdade ajuda | **Suporte** | Numero alto (> 7) |
    | Se a comunicacao esta boa | **Gap** | Numero negativo ou zero |
    | Se eles querem usar o NAP | **Intencao** | Numero alto (> 7) |
    | Se a divulgacao esta funcionando | **% Desconhecem** | Numero baixo (< 20%) |
    | Se quem usou aprovou | **Analise de Qualidade** | Numeros altos (> 8) |
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
# MATRIZ DE CORRELAÇÃO - DIVIDIDA POR BLOCOS
# ============================================================
st.markdown("---")
st.subheader("📊 Matriz de Correlação")
st.caption("🔍 **O que significa?** Valores próximos a 1 (vermelho) indicam que as perguntas tendem a subir juntas. Valores próximos a -1 (azul) indicam relação inversa.")

# Bloco 1: Percepção de necessidade e suporte
bloco1_cols = [
    "Já senti necessidade de apoio emocional durante a graduação.",
    "Eu me sentiria confortável em procurar ajuda dentro da instituição.",
    "Eu sinto que há suporte suficiente para dificuldades emocionais na faculdade.",
    "Acredito que serviços de apoio podem melhorar a experiência acadêmica dos alunos."
]

# Bloco 2: Intenção e confiança no NAP
bloco2_cols = [
    "Eu já pensei em utilizar o NAP (Núcleo de Apoio Psicopedagógico) em algum momento.",
    "Tenho confiança na confidencialidade do atendimento oferecido pelo NAP (Núcleo de Apoio Psicopedagógico)."
]

nomes_curtos_bloco1 = {
    "Já senti necessidade de apoio emocional durante a graduação.": "Necessidade",
    "Eu me sentiria confortável em procurar ajuda dentro da instituição.": "Conforto",
    "Eu sinto que há suporte suficiente para dificuldades emocionais na faculdade.": "Suporte",
    "Acredito que serviços de apoio podem melhorar a experiência acadêmica dos alunos.": "Crença"
}

nomes_curtos_bloco2 = {
    "Eu já pensei em utilizar o NAP (Núcleo de Apoio Psicopedagógico) em algum momento.": "Intenção",
    "Tenho confiança na confidencialidade do atendimento oferecido pelo NAP (Núcleo de Apoio Psicopedagógico).": "Confiança"
}

st.info("ℹ️ **Nota:** As perguntas sobre necessidade/suporte foram respondidas por um grupo de alunos, enquanto as perguntas sobre intenção/confiança foram respondidas por outro grupo. Por isso, não é possível calcular correlação entre esses blocos.")

# ============================================================
# BLOCO 1 - Necessidade e Suporte
# ============================================================
st.markdown("### Bloco 1: Necessidade, Conforto, Suporte e Crença")

cols_exist_bloco1 = [col for col in bloco1_cols if col in df.columns]

if len(cols_exist_bloco1) >= 2:
    # Limpar dados
    df_clean1 = df[cols_exist_bloco1].dropna()
    
    if len(df_clean1) >= 3:
        corr_matrix1 = df_clean1.corr()
        corr_matrix1 = corr_matrix1.rename(index=nomes_curtos_bloco1, columns=nomes_curtos_bloco1)
        
        mask1 = np.triu(np.ones_like(corr_matrix1, dtype=bool))
        corr_matrix_masked1 = corr_matrix1.mask(mask1)
        
        fig1 = px.imshow(
            corr_matrix_masked1,
            text_auto='.2f',
            aspect='auto',
            color_continuous_scale='RdBu_r',
            zmin=-1, zmax=1
        )
        fig1.update_layout(height=400)
        st.plotly_chart(fig1, use_container_width=True)
        
        st.caption(f"📊 Base: {len(df_clean1)} respostas completas")
    else:
        st.warning(f"Dados insuficientes para correlação")

# ============================================================
# BLOCO 2 - Intenção e Confiança
# ============================================================
st.markdown("### Bloco 2: Intenção e Confiança no NAP")

cols_exist_bloco2 = [col for col in bloco2_cols if col in df.columns]

if len(cols_exist_bloco2) >= 2:
    df_clean2 = df[cols_exist_bloco2].dropna()
    
    if len(df_clean2) >= 3:
        corr_matrix2 = df_clean2.corr()
        corr_matrix2 = corr_matrix2.rename(index=nomes_curtos_bloco2, columns=nomes_curtos_bloco2)
        
        mask2 = np.triu(np.ones_like(corr_matrix2, dtype=bool))
        corr_matrix_masked2 = corr_matrix2.mask(mask2)
        
        fig2 = px.imshow(
            corr_matrix_masked2,
            text_auto='.2f',
            aspect='auto',
            color_continuous_scale='RdBu_r',
            zmin=-1, zmax=1
        )
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)
        
        st.caption(f"📊 Base: {len(df_clean2)} respostas completas")
        
        # Mostrar valor específico
        if len(cols_exist_bloco2) == 2:
            col1, col2 = cols_exist_bloco2
            corr_value = df_clean2[col1].corr(df_clean2[col2])
            st.metric("Correlação entre Intenção e Confiança", f"{corr_value:.3f}")
    else:
        st.warning(f"Dados insuficientes para correlação")

with st.expander("📖 Como interpretar este gráfico"):
    st.markdown("""
    - **Vermelho (> 0.5)**: Perguntas positivamente relacionadas.
    - **Azul (< -0.5)**: Relação inversa.
    - **Próximo de zero**: Sem relação significativa.
    - **Bloco 1**: Correlações entre Necessidade, Conforto, Suporte e Crença.
    - **Bloco 2**: Correlação entre Intenção e Confiança.
    """)

# GUIA DE ANÁLISE INTERATIVO
st.markdown("---")
st.subheader("📈 Análise dos Dados - Clique e descubra")

st.markdown("💡 **Selecione uma correlação abaixo para entender o que ela significa:**")

# Criar abas para cada bloco
tab1, tab2, tab3 = st.tabs(["🔴 Bloco 1 - Necessidade/Suporte", "🟢 Bloco 2 - Intenção/Confiança", "🎯 Ações Prioritárias"])

# ============================================================
# TAB 1 - BLOCO 1
# ============================================================
with tab1:
    st.markdown("### Correlações entre Necessidade, Conforto, Suporte e Crença")
    
    # Grid de cards interativos (2x3)
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.markdown("#### 📌 Necessidade ↔ Conforto")
            st.markdown("**Valor:** 0.14 (Fraca positiva)")
            if st.button("🔍 O que significa?", key="btn_nec_conf"):
                st.info("""
                **Significado:** Quem sente necessidade de apoio tem POUCA tendência a se sentir confortável para pedir ajuda.
                
                **Problema:** Alunos que precisam ainda têm vergonha ou receio.
                
                **✅ Ação:** Trabalhar o estigma e normalizar pedir ajuda.
                """)
            
        with st.container(border=True):
            st.markdown("#### 📌 Necessidade ↔ Suporte")
            st.markdown("**Valor:** -0.19 (Fraca negativa)")
            if st.button("🔍 O que significa?", key="btn_nec_sup"):
                st.error("""
                **Significado:** Quanto MAIS o aluno precisa, MENOS ele percebe que a faculdade oferece suporte.
                
                **🔴 Este é um ALERTA!** O serviço existe mas não está sendo percebido.
                
                **✅ Ação:** COMUNICAR MAIS! Campanha de divulgação urgente.
                """)
            
        with st.container(border=True):
            st.markdown("#### 📌 Necessidade ↔ Crença")
            st.markdown("**Valor:** -0.09 (Quase zero)")
            if st.button("🔍 O que significa?", key="btn_nec_cre"):
                st.info("""
                **Significado:** Precisar de ajuda não faz acreditar mais ou menos que o serviço funciona.
                
                **Leitura:** O NAP é bem visto independentemente da necessidade do aluno.
                
                **✅ Ação:** Manter a boa reputação do serviço.
                """)
    
    with col2:
        with st.container(border=True):
            st.markdown("#### 📌 Conforto ↔ Suporte")
            st.markdown("**Valor:** 0.07 (Quase zero)")
            if st.button("🔍 O que significa?", key="btn_conf_sup"):
                st.info("""
                **Significado:** Sentir conforto para pedir ajuda não tem relação com perceber que há suporte.
                
                **Leitura:** São dimensões independentes. Um aluno pode se sentir confortável mas não saber que o suporte existe.
                
                **✅ Ação:** Trabalhar as duas frentes separadamente.
                """)
            
        with st.container(border=True):
            st.markdown("#### 📌 Conforto ↔ Crença")
            st.markdown("**Valor:** 0.35 (Moderada positiva)")
            if st.button("🔍 O que significa?", key="btn_conf_cre"):
                st.success("""
                **Significado:** Quem se sente confortável em pedir ajuda, ACREDITA mais que o serviço funciona.
                
                **✅ BOM SINAL!** Ambiente acolhedor aumenta a credibilidade do NAP.
                
                **✅ Ação:** Criar ambiente acolhedor e reduzir estigma. Depoimentos ajudam!
                """)
            
        with st.container(border=True):
            st.markdown("#### 📌 Suporte ↔ Crença")
            st.markdown("**Valor:** -0.05 (Quase zero)")
            if st.button("🔍 O que significa?", key="btn_sup_cre"):
                st.warning("""
                **Significado:** Perceber que há suporte não faz o aluno acreditar mais no serviço.
                
                **⚠️ Atenção:** Talvez os alunos vejam "suporte" como algo superficial ou burocrático.
                
                **✅ Ação:** Investigar o que os alunos entendem por "suporte" e melhorar a comunicação.
                """)

# ============================================================
# TAB 2 - BLOCO 2
# ============================================================
with tab2:
    st.markdown("### Correlação entre Intenção e Confiança")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.metric("📊 Correlação", "0.445", delta="Moderada positiva", delta_color="normal")
        
        st.markdown("**Força da correlação:**")
        st.progress(0.445, text="44.5%")
    
    with col2:
        if st.button("🔍 O que significa esta correlação?", key="btn_int_conf", use_container_width=True):
            st.success("""
            ### ✅ Significado:
            
            **Quem confia na confidencialidade do atendimento tem MAIS intenção de usar o NAP.**
            
            ---
            
            ### 🎯 O que fazer com isso:
            
            1. **Comunicar SIGILO** em todas as campanhas
            2. **Depoimentos** de quem usou o NAP
            3. **Transparência** sobre como os dados são tratados
            
            ---
            
            ### 📈 Expectativa:
            
            Aumentar a confiança em 1 ponto pode aumentar a intenção de uso em 0.44 pontos.
            """)
    
    with st.expander("❓ Por que não há correlação entre os blocos?"):
        st.markdown("""
        As perguntas sobre **Necessidade/Suporte** foram respondidas por um grupo de alunos (quem ainda não usou o NAP).  
        As perguntas sobre **Intenção/Confiança** foram respondidas por outro grupo.  
        
        **Resultado:** Não é possível calcular correlação entre os blocos porque nenhum aluno respondeu os dois conjuntos de perguntas.
        """)

# ============================================================
# TAB 3 - AÇÕES PRIORITÁRIAS
# ============================================================
with tab3:
    st.markdown("### 🎯 O que fazer com esses dados?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔴 URGENTE")
        with st.container(border=True):
            st.markdown("**1. Comunicar confidencialidade**")
            st.caption("Correlação: 0.445 (Intenção x Confiança)")
            st.checkbox("Criar material sobre sigilo", key="acao1")
            st.checkbox("Incluir no site/e-mail", key="acao2")
            
        with st.container(border=True):
            st.markdown("**2. Divulgar que o serviço existe**")
            st.caption("Correlação: -0.19 (Necessidade x Suporte)")
            st.checkbox("Campanha de divulgação geral", key="acao3")
            st.checkbox("Cartazes nos campi", key="acao4")
    
    with col2:
        st.markdown("#### 🟡 IMPORTANTE")
        with st.container(border=True):
            st.markdown("**3. Criar ambiente acolhedor**")
            st.caption("Correlação: 0.35 (Conforto x Crença)")
            st.checkbox("Reduzir estigma sobre saúde mental", key="acao5")
            st.checkbox("Treinar recepção e atendimento", key="acao6")
            
        with st.container(border=True):
            st.markdown("**4. Coletar depoimentos**")
            st.caption("Usuários do NAP aprovam o serviço")
            st.checkbox("Coletar depoimentos em vídeo", key="acao7")
            st.checkbox("Divulgar nas redes sociais", key="acao8")
    
    st.markdown("---")
    st.markdown("#### 📊 Marque as ações acima e acompanhe seu progresso:")
    
    checkboxes = ["acao1", "acao2", "acao3", "acao4", "acao5", "acao6", "acao7", "acao8"]
    marcadas = sum([st.session_state.get(cb, False) for cb in checkboxes])
    
    st.progress(marcadas / len(checkboxes), text=f"{marcadas} de {len(checkboxes)} ações planejadas")
    
    if marcadas == len(checkboxes):
        st.balloons()
        st.success("🎉 Parabéns! Todas as ações planejadas! Agora é executar!")

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
    evolucao = evolucao.sort_values('Semestre_Num')
    
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
    
    ordem = ['Não conhece NAP', 'Conhece mas não usou', 'Usou NAP']
    funil['Status'] = pd.Categorical(funil['Status'], categories=ordem, ordered=True)
    funil = funil.sort_values('Status')
    
    fig = px.bar(funil, x='Status', y='Quantidade', color='Status', text='Quantidade')
    fig.update_layout(showlegend=False)
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
    
    1. **Comunicação é a prioridade máxima:** {int(pct_nao)}% dos alunos desconhecem o NAP.
    2. **Gap de {gap:.1f} pontos:** Alunos precisam de apoio ({necessidade:.1f}/10) mas não percebem que a faculdade oferece ({suporte:.1f}/10).
    3. **Quem usa, aprova:** As avaliações dos usuários são positivas.
    
    ### Recomendações:
    
    - Campanha de divulgação imediata
    - Comunicar claramente os serviços oferecidos
    - Coletar e divulgar depoimentos de alunos que usaram
    - Acompanhar evolução do gap semestralmente
    """)

st.caption(f"📊 Dashboard atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | Base: {len(df)} alunos")
