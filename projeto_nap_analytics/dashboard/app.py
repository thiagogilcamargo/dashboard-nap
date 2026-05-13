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
# VERIFICAÇÃO DE DADOS
# ============================================================
if df.empty:
    st.error("❌ Não foi possível carregar os dados. Verifique o arquivo dados.csv")
    st.stop()

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
# BLOCO 1 - Necessidade e Suporte (DINÂMICO)
# ============================================================
st.markdown("### Bloco 1: Necessidade, Conforto, Suporte e Crença")

cols_exist_bloco1 = [col for col in bloco1_cols if col in df.columns]

if len(cols_exist_bloco1) >= 2:
    # Limpar dados
    df_clean1 = df[cols_exist_bloco1].dropna()
    
    if len(df_clean1) >= 3:
        # Matriz de correlação
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
else:
    st.warning("Colunas necessárias não encontradas no dataset")

# ============================================================
# BLOCO 2 - Intenção e Confiança (DINÂMICO)
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
else:
    st.warning("Colunas necessárias não encontradas no dataset")

with st.expander("📖 Como interpretar este gráfico"):
    st.markdown("""
    - **Vermelho (> 0.5)**: Perguntas positivamente relacionadas.
    - **Azul (< -0.5)**: Relação inversa.
    - **Próximo de zero**: Sem relação significativa.
    - **Bloco 1**: Correlações entre Necessidade, Conforto, Suporte e Crença.
    - **Bloco 2**: Correlação entre Intenção e Confiança.
    """)

# ============================================================
# GUIA DE ANÁLISE INTERATIVO (VERSÃO DINÂMICA)
# ============================================================
st.markdown("---")
st.subheader("📈 Análise dos Dados - Clique e descubra")

st.markdown("💡 **Selecione uma correlação abaixo para entender o que ela significa:**")

# Criar abas para cada bloco
tab1, tab2, tab3 = st.tabs(["🔴 Bloco 1 - Necessidade/Suporte", "🟢 Bloco 2 - Intenção/Confiança", "🎯 Ações Prioritárias"])

# ============================================================
# TAB 1 - BLOCO 1 (VERSÃO DINÂMICA)
# ============================================================
with tab1:
    st.markdown("### Correlações entre Necessidade, Conforto, Suporte e Crença")
    
    if len(cols_exist_bloco1) >= 2 and len(df_clean1) >= 3:
        # Calcular correlações reais
        corr_real = df_clean1.corr()
        
        # Lista de pares para análise
        pares = [
            ("Já senti necessidade de apoio emocional durante a graduação.", 
             "Eu me sentiria confortável em procurar ajuda dentro da instituição."),
            ("Já senti necessidade de apoio emocional durante a graduação.",
             "Eu sinto que há suporte suficiente para dificuldades emocionais na faculdade."),
            ("Já senti necessidade de apoio emocional durante a graduação.",
             "Acredito que serviços de apoio podem melhorar a experiência acadêmica dos alunos."),
            ("Eu me sentiria confortável em procurar ajuda dentro da instituição.",
             "Eu sinto que há suporte suficiente para dificuldades emocionais na faculdade."),
            ("Eu me sentiria confortável em procurar ajuda dentro da instituição.",
             "Acredito que serviços de apoio podem melhorar a experiência acadêmica dos alunos."),
            ("Eu sinto que há suporte suficiente para dificuldades emocionais na faculdade.",
             "Acredito que serviços de apoio podem melhorar a experiência acadêmica dos alunos.")
        ]
        
        nomes_exibicao = [
            ("Necessidade", "Conforto"),
            ("Necessidade", "Suporte"),
            ("Necessidade", "Crença"),
            ("Conforto", "Suporte"),
            ("Conforto", "Crença"),
            ("Suporte", "Crença")
        ]
        
        col1, col2 = st.columns(2)
        
        for i, ((col_a, col_b), (nome_a, nome_b)) in enumerate(zip(pares, nomes_exibicao)):
            if col_a in corr_real.index and col_b in corr_real.columns:
                corr_val = corr_real.loc[col_a, col_b]
                
                with (col1 if i < 3 else col2):
                    with st.container(border=True):
                        st.markdown(f"#### 📌 {nome_a} ↔ {nome_b}")
                        
                        # Cor da métrica baseada no valor
                        if corr_val > 0.3:
                            st.markdown(f"**Valor:** :green[{corr_val:.2f}] (Moderada positiva)")
                        elif corr_val < -0.3:
                            st.markdown(f"**Valor:** :red[{corr_val:.2f}] (Moderada negativa)")
                        else:
                            st.markdown(f"**Valor:** :gray[{corr_val:.2f}] (Fraca)")
                        
                        if st.button(f"🔍 O que significa?", key=f"btn_din_{i}"):
                            if nome_a == "Necessidade" and nome_b == "Conforto":
                                if corr_val < 0.2:
                                    st.info("""
                                    **Significado:** Quem sente necessidade de apoio tem POUCA tendência a se sentir confortável para pedir ajuda.
                                    
                                    **Problema:** Alunos que precisam ainda têm vergonha ou receio.
                                    
                                    **✅ Ação:** Trabalhar o estigma e normalizar pedir ajuda.
                                    """)
                                else:
                                    st.success("""
                                    **Significado:** Alunos que precisam se sentem confortáveis para pedir ajuda.
                                    
                                    **✅ BOM SINAL!** Ambiente acolhedor.
                                    """)
                            
                            elif nome_a == "Necessidade" and nome_b == "Suporte":
                                if corr_val < -0.1:
                                    st.error("""
                                    **Significado:** Quanto MAIS o aluno precisa, MENOS ele percebe que a faculdade oferece suporte.
                                    
                                    **🔴 ALERTA!** O serviço existe mas não está sendo percebido.
                                    
                                    **✅ Ação:** COMUNICAR MAIS! Campanha de divulgação urgente.
                                    """)
                                else:
                                    st.info("""
                                    **Significado:** Necessidade e percepção de suporte são independentes.
                                    
                                    **✅ Ação:** Manter comunicação sobre os serviços disponíveis.
                                    """)
                            
                            elif nome_a == "Necessidade" and nome_b == "Crença":
                                st.info("""
                                **Significado:** Precisar de ajuda não faz acreditar mais ou menos que o serviço funciona.
                                
                                **Leitura:** O NAP é bem visto independentemente da necessidade do aluno.
                                
                                **✅ Ação:** Manter a boa reputação do serviço.
                                """)
                            
                            elif nome_a == "Conforto" and nome_b == "Suporte":
                                if corr_val > 0.3:
                                    st.success("""
                                    **Significado:** Ambientes acolhedores aumentam a percepção de suporte.
                                    
                                    **✅ Ação:** Investir em atendimento humanizado.
                                    """)
                                else:
                                    st.info("""
                                    **Significado:** Sentir conforto para pedir ajuda não tem relação com perceber que há suporte.
                                    
                                    **✅ Ação:** Trabalhar as duas frentes separadamente.
                                    """)
                            
                            elif nome_a == "Conforto" and nome_b == "Crença":
                                if corr_val > 0.3:
                                    st.success(f"""
                                    **Significado:** Quem se sente confortável em pedir ajuda, ACREDITA mais que o serviço funciona (r={corr_val:.2f}).
                                    
                                    **✅ BOM SINAL!** Ambiente acolhedor aumenta a credibilidade do NAP.
                                    
                                    **✅ Ação:** Criar ambiente acolhedor e reduzir estigma.
                                    """)
                                else:
                                    st.info("""
                                    **Significado:** Conforto e crença no serviço são independentes.
                                    """)
                            
                            elif nome_a == "Suporte" and nome_b == "Crença":
                                st.warning("""
                                **Significado:** Perceber que há suporte não faz o aluno acreditar mais no serviço.
                                
                                **⚠️ Atenção:** Talvez os alunos vejam "suporte" como algo superficial.
                                
                                **✅ Ação:** Investigar o que os alunos entendem por "suporte".
                                """)
    else:
        st.warning("Dados insuficientes para análise de correlação")

# ============================================================
# TAB 2 - BLOCO 2 (VERSÃO DINÂMICA)
# ============================================================
with tab2:
    st.markdown("### Correlação entre Intenção e Confiança")
    
    if len(cols_exist_bloco2) >= 2 and len(df_clean2) >= 3:
        col1_int, col2_int = cols_exist_bloco2[0], cols_exist_bloco2[1]
        corr_int_conf = df_clean2[col1_int].corr(df_clean2[col2_int])
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Cor da métrica baseada no valor
            if corr_int_conf > 0.3:
                st.metric("📊 Correlação", f"{corr_int_conf:.3f}", delta="Moderada positiva", delta_color="normal")
            elif corr_int_conf < 0:
                st.metric("📊 Correlação", f"{corr_int_conf:.3f}", delta="Negativa", delta_color="inverse")
            else:
                st.metric("📊 Correlação", f"{corr_int_conf:.3f}", delta="Fraca positiva", delta_color="off")
            
            st.markdown("**Força da correlação:**")
            st.progress(min(abs(corr_int_conf), 1.0), text=f"{abs(corr_int_conf)*100:.1f}%")
        
        with col2:
            if st.button("🔍 O que significa esta correlação?", key="btn_int_conf_din", use_container_width=True):
                if corr_int_conf > 0.3:
                    st.success(f"""
                    ### ✅ Significado:
                    
                    **Quem confia na confidencialidade tem MAIS intenção de usar o NAP (r={corr_int_conf:.3f}).**
                    
                    ---
                    
                    ### 🎯 O que fazer com isso:
                    
                    1. **Comunicar SIGILO** em todas as campanhas
                    2. **Depoimentos** de quem usou o NAP
                    3. **Transparência** sobre como os dados são tratados
                    """)
                elif corr_int_conf > 0:
                    st.info(f"""
                    ### ℹ️ Significado:
                    
                    **Há uma leve tendência positiva (r={corr_int_conf:.3f}).**
                    
                    Confiança influencia intenção, mas outros fatores também são importantes.
                    
                    ### 🎯 Ações recomendadas:
                    
                    - Fortalecer comunicação sobre sigilo
                    - Coletar feedback sobre barreiras de uso
                    """)
                else:
                    st.warning(f"""
                    ### ⚠️ Significado:
                    
                    **Correlação negativa ou próxima de zero (r={corr_int_conf:.3f}).**
                    
                    Confiança no sigilo NÃO está relacionada com intenção de usar.
                    
                    ### 🔍 Investigar:
                    
                    - Quais são as reais barreiras de acesso?
                    - Falta de tempo? Desconhecimento? Outros motivos?
                    """)
        
        with st.expander("❓ Por que não há correlação entre os blocos?"):
            st.markdown("""
            As perguntas sobre **Necessidade/Suporte** foram respondidas por um grupo de alunos (quem ainda não usou o NAP).  
            As perguntas sobre **Intenção/Confiança** foram respondidas por outro grupo.  
            
            **Resultado:** Não é possível calcular correlação entre os blocos porque nenhum aluno respondeu os dois conjuntos de perguntas.
            """)
    else:
        st.warning("Dados insuficientes para análise de correlação")

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
            if len(cols_exist_bloco2) >= 2 and len(df_clean2) >= 3:
                corr_val = df_clean2[cols_exist_bloco2[0]].corr(df_clean2[cols_exist_bloco2[1]])
                st.caption(f"Correlação: {corr_val:.3f} (Intenção x Confiança)")
            st.checkbox("Criar material sobre sigilo", key="acao1")
            st.checkbox("Incluir no site/e-mail", key="acao2")
            
        with st.container(border=True):
            st.markdown("**2. Divulgar que o serviço existe**")
            st.caption(f"Gap: {gap:.1f} pontos | {pct_nao:.0f}% desconhecem")
            st.checkbox("Campanha de divulgação geral", key="acao3")
            st.checkbox("Cartazes nos campi", key="acao4")
    
    with col2:
        st.markdown("#### 🟡 IMPORTANTE")
        with st.container(border=True):
            st.markdown("**3. Criar ambiente acolhedor**")
            st.caption("Reduzir estigma sobre saúde mental")
            st.checkbox("Treinar recepção e atendimento", key="acao5")
            st.checkbox("Criar canais anônimos de acolhimento", key="acao6")
            
        with st.container(border=True):
            st.markdown("**4. Coletar depoimentos**")
            st.caption(f"{pct_usou:.0f}% dos alunos usaram o NAP")
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
# PRIORIZAÇÃO (VERSÃO DINÂMICA)
# ============================================================
st.markdown("---")
st.subheader("🎯 Priorização de Problemas")
st.caption("🔍 **O que mostra?** Prioridade = Impacto / Esforço. Quanto maior a barra, mais urgente é resolver o problema.")

problemas = []

# Problema 1: Falta de informação
col_info = None
for col in df.columns:
    if 'sei a quem recorrer' in col.lower() or 'acessar' in col.lower():
        col_info = col
        break

if col_info:
    dados = pd.to_numeric(df[col_info], errors='coerce').dropna()
    if len(dados) > 0:
        # Quanto menos sabe, maior o impacto
        impacto_info = 10 - dados.mean()
        esforco_info = 2  # Baixo esforço
        problemas.append({"Problema": "Falta de informação", "Impacto": impacto_info, "Esforço": esforco_info})

# Problema 2: Preconceito
col_prec = None
for col in df.columns:
    if 'preconceito' in col.lower() or 'estigma' in col.lower():
        col_prec = col
        break

if col_prec:
    dados = pd.to_numeric(df[col_prec], errors='coerce').dropna()
    if len(dados) > 0:
        impacto_prec = dados.mean()
        esforco_prec = 6  # Esforço médio-alto
        problemas.append({"Problema": "Preconceito/Estigma", "Impacto": impacto_prec, "Esforço": esforco_prec})

# Problema 3: Gap
if gap > 2:
    # Esforço dinâmico baseado na magnitude do gap
    if gap > 5:
        esforco_gap = 8
    elif gap > 3:
        esforco_gap = 6
    else:
        esforco_gap = 4
    problemas.append({"Problema": f"Gap de {gap:.1f} pontos", "Impacto": gap, "Esforço": esforco_gap})

# Problema 4: Desconhecimento do NAP
if pct_nao > 20:
    impacto_desc = pct_nao / 10  # Normalizado
    esforco_desc = 3  # Esforço baixo-médio
    problemas.append({"Problema": f"{pct_nao:.0f}% desconhecem NAP", "Impacto": impacto_desc, "Esforço": esforco_desc})

if problemas:
    df_problemas = pd.DataFrame(problemas)
    df_problemas['Prioridade'] = df_problemas['Impacto'] / df_problemas['Esforço']
    df_problemas = df_problemas.sort_values('Prioridade', ascending=False)
    
    fig_prior = px.bar(df_problemas, x='Problema', y='Prioridade', color='Problema', text=df_problemas['Prioridade'].round(2))
    fig_prior.update_layout(showlegend=False)
    st.plotly_chart(fig_prior, use_container_width=True)
    
    with st.expander("📖 Como interpretar este gráfico"):
        st.markdown("""
        - **Prioridade mais alta** = maior relação Impacto/Esforço
        - **Falta de informação** tem alto impacto e baixo esforço → PRIORIDADE MÁXIMA
        - **Desconhecimento do NAP** requer campanha de divulgação
        - **Gap** é um problema estrutural que exige ação coordenada
        - **Preconceito** tem esforço alto (mudança cultural demora)
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
    fig.update_layout(showlegend=False)
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
