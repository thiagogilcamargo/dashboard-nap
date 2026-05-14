
| Resultado | Significado |
|-----------|-------------|
| **Gap positivo (+)** | Alunos precisam mais do que percebem -> **FALTA DE COMUNICACAO** |
| **Gap negativo (-)** | Suporte excede necessidade -> **SITUACAO IDEAL** |
| **Gap proximo de zero** | Necessidade e suporte estao alinhados |

---

### 🟢 **Sinais VERDES (bom)**
- Suporte alto (> 7)
- Crenca alta (> 8)
- Gap negativo
- Intencao alta (> 7)
- Poucos desconhecem NAP (< 20%)

### 🔴 **Sinais VERMELHOS (alerta)**
- Necessidade alta (> 7)
- Suporte baixo (< 5)
- Gap positivo (> 3)
- Mais de 40% desconhecem NAP

---

### 📖 **Como usar**
1. **Filtros na lateral esquerda** -> Selecione campus, periodo, genero
2. **KPIs coloridos** -> Visao geral rapida
3. **Alertas automaticos** -> Problemas identificados
4. **Correlacoes** -> Relacoes entre perguntas
5. **Funil de adocao** -> Quantos alunos em cada etapa
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
# VERIFICAÇÃO DE DADOS
# ============================================================
if df.empty:
st.error("❌ Não foi possível carregar os dados. Verifique o arquivo dados.csv")
st.stop()

def gerar_html_relatorio(df):
    necessidade = df['score_necessidade'].mean() if 'score_necessidade' in df.columns else 0
    suporte = df['score_suporte'].mean() if 'score_suporte' in df.columns else 0
    gap = df['score_gap'].mean() if 'score_gap' in df.columns else 0
    intencao = df['score_intencao'].mean() if 'score_intencao' in df.columns else 0
    pct_usou = (df['Jornada'] == 'Usou NAP').mean() * 100 if 'Jornada' in df.columns else 0
    pct_conhece = (df['Jornada'] == 'Conhece mas não usou').mean() * 100 if 'Jornada' in df.columns else 0
    pct_nao = (df['Jornada'] == 'Não conhece NAP').mean() * 100 if 'Jornada' in df.columns else 0
    
    html = f"""
    <html>
    <body>
    <h1>NAP - Relatorio Executivo</h1>
    <p>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
    <p>Total: {len(df)} alunos</p>
    <p>Usaram o NAP: {round(pct_usou)}%</p>
    <p>Necessidade: {round(necessidade, 1)}/10</p>
    <p>Suporte: {round(suporte, 1)}/10</p>
    <p>Gap: {round(gap, 1)}</p>
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

st.info("ℹ️ As perguntas de diferentes blocos foram respondidas por grupos diferentes, por isso não calculamos correlação entre elas.")

# ============================================================
# FUNIL DE ADOÇÃO
# ============================================================
st.markdown("---")
st.subheader("📊 Funil de Adoção")
st.caption("🔍 Quantos alunos estão em cada etapa da jornada.")

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

1. **Comunicacao é a prioridade maxima:** {pct_nao:.0f}% dos alunos desconhecem o NAP.
2. **Gap de {gap:.1f} pontos:** Alunos precisam de apoio ({necessidade:.1f}/10) mas nao percebem que a faculdade oferece ({suporte:.1f}/10).
3. **Quem usa, aprova:** As avaliacoes dos usuarios sao positivas.

### Recomendacoes:

- ✅ Campanha de divulgacao imediata
- ✅ Comunicar claramente os servicos oferecidos
- ✅ Coletar e divulgar depoimentos de alunos que usaram
- ✅ Acompanhar evolucao do gap semestralmente
""")

st.caption(f"📊 Dashboard atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | Base: {len(df)} alunos")
