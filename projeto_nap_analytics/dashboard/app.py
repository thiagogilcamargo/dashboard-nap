# ============================================================
# KPIs (VISÃO GERAL) - VERSÃO LIMPA
# ============================================================
st.subheader("📊 Visão Geral")

# Calcular as médias (NaN são ignorados automaticamente)
necessidade = df['score_necessidade'].mean() if 'score_necessidade' in df.columns else np.nan
suporte = df['score_suporte'].mean() if 'score_suporte' in df.columns else np.nan
gap = df['score_gap'].mean() if 'score_gap' in df.columns else np.nan
intencao = df['score_intencao'].mean() if 'score_intencao' in df.columns else np.nan

# Mostrar aviso se dados são insuficientes
if pd.isna(necessidade):
    st.warning("⚠️ Dados insuficientes para calcular Necessidade de apoio")
    necessidade = 0
if pd.isna(suporte):
    st.warning("⚠️ Dados insuficientes para calcular Suporte percebido")
    suporte = 0
if pd.isna(intencao):
    st.warning("⚠️ Dados insuficientes para calcular Intenção de uso")
    intencao = 0

pct_usou = (df['Jornada'] == 'Usou NAP').mean() * 100 if 'Jornada' in df.columns else 0
pct_conhece = (df['Jornada'] == 'Conhece mas não usou').mean() * 100 if 'Jornada' in df.columns else 0
pct_nao_conhece = (df['Jornada'] == 'Não conhece NAP').mean() * 100 if 'Jornada' in df.columns else 0

# Criar 8 colunas
col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

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
