# Substitua o bloco dos KPIs (col3, col4, col5) por:

with col3:
    if 'score_necessidade' in df.columns and df['score_necessidade'].mean() > 0:
        st.metric("🎯 Necessidade de apoio", f"{df['score_necessidade'].mean():.1f}/10")
    else:
        st.metric("🎯 Necessidade de apoio", "0.0/10")

with col4:
    if 'score_suporte' in df.columns and df['score_suporte'].mean() > 0:
        st.metric("🏫 Suporte percebido", f"{df['score_suporte'].mean():.1f}/10")
    else:
        st.metric("🏫 Suporte percebido", "0.0/10")

with col5:
    if 'score_gap' in df.columns and df['score_gap'].mean() > 0:
        gap = df['score_gap'].mean()
        cor = "🔴" if gap > 3 else "🟡" if gap > 1 else "🟢"
        st.metric(f"{cor} Gap (Necessidade - Suporte)", f"{gap:.1f}")
    else:
        st.metric("📊 Gap", "0.0")
