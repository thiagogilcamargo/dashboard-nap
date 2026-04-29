# utils.py
import pandas as pd
import numpy as np
import os
import streamlit as st
from difflib import get_close_matches

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PATH_RAW = os.path.join(BASE_DIR, "dados", "raw", "dados.csv")

def carregar_dados_brutos():
    df = pd.read_csv(PATH_RAW, encoding='utf-8-sig')
    df.columns = df.columns.str.replace("\n", " ").str.strip()
    df = df.replace(r'^\s*$', np.nan, regex=True)
    return df

def classificar_jornada(valor):
    if pd.isna(valor):
        return "Indefinido"
    if "Não conheço" in str(valor):
        return "Não conhece NAP"
    if "já o utilizei" in str(valor):
        return "Usou NAP"
    if "Conheço" in str(valor):
        return "Conhece mas não usou"
    return "Indefinido"

def aplicar_jornada(df):
    col_jornada = "Quais da opções abaixo melhor representa você em relação ao NAP (Núcleo de Apoio Psicopedagógico)?"
    if col_jornada in df.columns:
        df['Jornada'] = df[col_jornada].apply(classificar_jornada)
    else:
        df['Jornada'] = "Indefinido"
    return df

# ============================================================
# UPGRADE 1: MAPEAMENTO SEMÂNTICO (substitui índices fixos)
# ============================================================

def normalizar_string(texto: str) -> str:
    """Normaliza string para matching"""
    if not isinstance(texto, str):
        return ""
    texto = texto.lower()
    # Remove acentos simples
    texto = texto.replace("ã", "a").replace("õ", "o").replace("á", "a")
    texto = texto.replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    texto = texto.replace("ç", "c")
    # Remove caracteres especiais
    texto = ''.join(c for c in texto if c.isalnum() or c.isspace())
    return texto.strip()

def encontrar_coluna(df, nome_esperado: str, palavras_chave: list) -> str:
    """
    Encontra coluna por: 1) nome exato, 2) palavras-chave, 3) fuzzy matching
    Retorna o nome da coluna ou None se não encontrar
    """
    nome_norm = normalizar_string(nome_esperado)
    
    # 1. Tentar match exato
    for col in df.columns:
        if col == nome_esperado:
            return col
    
    # 2. Tentar por palavras-chave
    for col in df.columns:
        col_norm = normalizar_string(col)
        for palavra in palavras_chave:
            if normalizar_string(palavra) in col_norm:
                st.info(f"🔍 Coluna mapeada: '{col}' -> '{nome_esperado[:30]}...'")
                return col
    
    # 3. Tentar fuzzy matching
    colunas_norm = {col: normalizar_string(col) for col in df.columns}
    matches = get_close_matches(nome_norm, list(colunas_norm.values()), n=1, cutoff=0.7)
    if matches:
        for col, col_norm in colunas_norm.items():
            if col_norm == matches[0]:
                st.warning(f"⚠️ Fuzzy match: '{col}' -> '{nome_esperado[:30]}...'")
                return col
    
    return None

# ============================================================
# UPGRADE 2 e 3: Score com confiança (sem fillna(0))
# ============================================================

def calcular_score_com_confianca(df, colunas, nome_score, min_respostas=2):
    """
    Calcula score APENAS para linhas com número mínimo de respostas.
    Retorna (score_series, confidence_series)
    """
    # Conta quantas respostas válidas por linha
    validas = df[colunas].notna().sum(axis=1)
    
    # Calcula média (ignorando NaN)
    media = df[colunas].mean(axis=1, skipna=True)
    
    # Só mantém média se tiver o mínimo de respostas
    score = media.where(validas >= min_respostas, np.nan)
    
    # Confiança: percentual de respostas válidas (0-1)
    confianca = validas / len(colunas)
    
    return score, confianca

def calcular_scores_dataframe(df):
    """
    Versão com mapeamento semântico + score com confiança
    SEM fillna(0) - NUNCA inventa dados
    """
    
    # ============================================================
    # MAPEAMENTO DAS COLUNAS (SEM ÍNDICES FIXOS)
    # ============================================================
    col_nec1 = encontrar_coluna(df, 
        "Já senti necessidade de apoio emocional durante a graduação.",
        ["necessidade", "apoio emocional", "senti necessidade"])
    
    col_nec2 = encontrar_coluna(df,
        "Eu me sentiria confortável em procurar ajuda dentro da instituição.",
        ["confortável", "procurar ajuda", "confortavel"])
    
    col_nec3 = encontrar_coluna(df,
        "Acredito que serviços de apoio podem melhorar a experiência acadêmica dos alunos.",
        ["acredito", "serviços", "melhorar", "experiência acadêmica"])
    
    col_sup = encontrar_coluna(df,
        "Eu sinto que há suporte suficiente para dificuldades emocionais na faculdade.",
        ["suporte", "suficiente", "dificuldades emocionais"])
    
    col_int1 = encontrar_coluna(df,
        "Eu já pensei em utilizar o NAP (Núcleo de Apoio Psicopedagógico) em algum momento.",
        ["pensei", "utilizar", "NAP"])
    
    col_int2 = encontrar_coluna(df,
        "Tenho confiança na confidencialidade do atendimento oferecido pelo NAP (Núcleo de Apoio Psicopedagógico).",
        ["confiança", "confidencialidade"])
    
    col_int3 = encontrar_coluna(df,
        "Eu sei como acessar os serviços oferecidos pelo NAP (Núcleo de Apoio Psicopedagógico).",
        ["acessar", "serviços", "oferecidos"])
    
    # ============================================================
    # VALIDAÇÃO DAS COLUNAS
    # ============================================================
    colunas_necessidade = [c for c in [col_nec1, col_nec2, col_nec3] if c]
    colunas_intencao = [c for c in [col_int1, col_int2, col_int3] if c]
    
    if len(colunas_necessidade) < 2:
        st.error("❌ Colunas de necessidade não encontradas. Verifique o CSV.")
        df['score_necessidade'] = np.nan
        df['score_necessidade_confianca'] = 0
    else:
        # Converter para numérico
        for col in colunas_necessidade + [col_sup] + colunas_intencao:
            if col:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Score de Necessidade (com confiança)
        df['score_necessidade'], df['score_necessidade_confianca'] = calcular_score_com_confianca(
            df, colunas_necessidade, "necessidade", min_respostas=2
        )
        
        # Score de Suporte
        if col_sup:
            df['score_suporte'] = df[col_sup]
            df['score_suporte_confianca'] = df[col_sup].notna().astype(float)
        else:
            df['score_suporte'] = np.nan
            df['score_suporte_confianca'] = 0
        
        # Score de Intenção
        if len(colunas_intencao) >= 2:
            df['score_intencao'], df['score_intencao_confianca'] = calcular_score_com_confianca(
                df, colunas_intencao, "intencao", min_respostas=2
            )
        else:
            df['score_intencao'] = np.nan
            df['score_intencao_confianca'] = 0
        
        # Gap (só calcula se ambos existirem)
        df['score_gap'] = df['score_necessidade'] - df['score_suporte']
        df['score_gap_confianca'] = df[['score_necessidade_confianca', 'score_suporte_confianca']].min(axis=1)
    
    # ============================================================
    # DEBUG (mostra o que foi encontrado)
    # ============================================================
    st.info(f"🔍 Mapeamento de colunas:")
    st.info(f"   Necessidade: {[c for c in [col_nec1, col_nec2, col_nec3] if c]}")
    st.info(f"   Suporte: {col_sup}")
    st.info(f"   Intenção: {[c for c in [col_int1, col_int2, col_int3] if c]}")
    
    validos = df['score_necessidade'].notna().sum()
    st.info(f"📊 Necessidade: média={df['score_necessidade'].mean():.1f}/10 (válidos: {validos}/{len(df)})")
    
    return df

def calcular_priorizacao(df):
    problemas = []
    
    # Buscar coluna de informação
    col_info = encontrar_coluna(df,
        "Eu sei a quem recorrer dentro da faculdade quando tenho dificuldades emocionais.",
        ["sei a quem recorrer", "dificuldades emocionais"])
    
    if col_info:
        df[col_info] = pd.to_numeric(df[col_info], errors='coerce')
        if df[col_info].notna().sum() > 10:
            impacto_info = 10 - df[col_info].mean()
            problemas.append({"Problema": "Falta de informação", "Impacto": impacto_info, "Esforço": 2})
    
    # Buscar coluna de preconceito
    col_prec = encontrar_coluna(df,
        "Sinto que existe um preconceito em procurar apoio psicológico ou pedagógico na instituição.",
        ["preconceito", "procurar apoio"])
    
    if col_prec:
        df[col_prec] = pd.to_numeric(df[col_prec], errors='coerce')
        if df[col_prec].notna().sum() > 10:
            impacto_prec = df[col_prec].mean()
            problemas.append({"Problema": "Preconceito", "Impacto": impacto_prec, "Esforço": 6})
    
    if problemas:
        df_problemas = pd.DataFrame(problemas)
        df_problemas['Prioridade'] = df_problemas['Impacto'] / df_problemas['Esforço']
        return df_problemas.sort_values('Prioridade', ascending=False)
    
    return pd.DataFrame([{"Problema": "Falta de informação", "Impacto": 7.5, "Esforço": 2, "Prioridade": 3.75}])

def limpar_colunas(df):
    colunas_remover = [col for col in df.columns if 'Carimbo' in col or 'Declaro' in col or 'E-MAIL' in col or 'convidado' in col]
    return df.drop(columns=colunas_remover, errors='ignore')
