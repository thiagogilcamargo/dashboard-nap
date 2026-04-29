# utils.py
import pandas as pd
import numpy as np
import os
import streamlit as st

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PATH_RAW = os.path.join(BASE_DIR, "dados", "raw", "dados.csv")

# Importa as configurações
from config.config import (
    NECESSIDADE_COLS, 
    SUPORTE_COLS, 
    INTENCAO_COLS, 
    JORNADA_COL
)

def carregar_dados_brutos():
    """Carrega e limpa os dados brutos"""
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
    if JORNADA_COL in df.columns:
        df['Jornada'] = df[JORNADA_COL].apply(classificar_jornada)
    else:
        df['Jornada'] = "Indefinido"
    return df

def validar_colunas(df, colunas, contexto):
    """Valida se todas as colunas existem no DataFrame"""
    faltando = [col for col in colunas if col not in df.columns]
    if faltando:
        st.error(f"❌ {contexto}: Colunas não encontradas: {faltando}")
        return False
    return True

def calcular_scores_dataframe(df):
    """Calcula todos os scores com validação rigorosa"""
    
    # 1. Validar colunas de Necessidade
    if not validar_colunas(df, NECESSIDADE_COLS, "Necessidade"):
        st.stop()
    
    # 2. Validar colunas de Suporte
    if not validar_colunas(df, SUPORTE_COLS, "Suporte"):
        st.stop()
    
    # 3. Validar colunas de Intenção
    if not validar_colunas(df, INTENCAO_COLS, "Intenção"):
        st.stop()
    
    # 4. Converter para numérico (SEM fillna, preservar NaN)
    for col in NECESSIDADE_COLS + SUPORTE_COLS + INTENCAO_COLS:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 5. Calcular scores
    df['score_necessidade'] = df[NECESSIDADE_COLS].mean(axis=1, skipna=True)
    df['score_suporte'] = df[SUPORTE_COLS[0]]
    df['score_intencao'] = df[INTENCAO_COLS].mean(axis=1, skipna=True)
    df['score_gap'] = df['score_necessidade'] - df['score_suporte']
    
    # 6. Debug info (mostra no Streamlit)
    st.info(f"📊 Scores calculados:")
    st.info(f"   Necessidade: {df['score_necessidade'].mean():.1f}/10")
    st.info(f"   Suporte: {df['score_suporte'].mean():.1f}/10")
    st.info(f"   Gap: {df['score_gap'].mean():.1f}")
    st.info(f"   Intenção: {df['score_intencao'].mean():.1f}/10")
    
    return df

def calcular_priorizacao(df):
    """Calcula priorização com base em colunas conhecidas"""
    problemas = []
    
    col_info = "Eu sei a quem recorrer dentro da faculdade quando tenho dificuldades emocionais."
    if col_info in df.columns:
        df[col_info] = pd.to_numeric(df[col_info], errors='coerce')
        impacto_info = 10 - df[col_info].mean()
        problemas.append({"Problema": "Falta de informação", "Impacto": impacto_info, "Esforço": 2})
    
    col_prec = "Sinto que existe um preconceito em procurar apoio psicológico ou pedagógico na instituição."
    if col_prec in df.columns:
        df[col_prec] = pd.to_numeric(df[col_prec], errors='coerce')
        impacto_prec = df[col_prec].mean()
        problemas.append({"Problema": "Preconceito", "Impacto": impacto_prec, "Esforço": 6})
    
    if problemas:
        df_problemas = pd.DataFrame(problemas)
        df_problemas['Prioridade'] = df_problemas['Impacto'] / df_problemas['Esforço']
        return df_problemas.sort_values('Prioridade', ascending=False)
    
    # Fallback padrão
    return pd.DataFrame([{"Problema": "Falta de informação", "Impacto": 7.5, "Esforço": 2, "Prioridade": 3.75}])

def limpar_colunas(df):
    """Remove apenas colunas claramente desnecessárias"""
    colunas_remover = [col for col in df.columns if 'Carimbo' in col or 'Declaro' in col or 'E-MAIL' in col or 'convidado' in col]
    return df.drop(columns=colunas_remover, errors='ignore')
