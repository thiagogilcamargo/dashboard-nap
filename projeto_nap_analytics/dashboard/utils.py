# dashboard/utils.py
import pandas as pd
import numpy as np
import os
import streamlit as st

# IMPORTAR DO CONFIG
from dashboard.config import (
    PATH_RAW,
    JORNADA_COL,
    NECESSIDADE_COLS,
    SUPORTE_COLS,
    INTENCAO_COLS
)

# ============================================================
# LOAD
# ============================================================
def carregar_dados_brutos():
    df = pd.read_csv(PATH_RAW, encoding="utf-8-sig")
    df.columns = df.columns.str.replace("\n", " ").str.strip()
    df = df.replace(r"^\s*$", np.nan, regex=True)
    return df

# ============================================================
# JORNADA
# ============================================================
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
        df["Jornada"] = df[JORNADA_COL].apply(classificar_jornada)
    else:
        df["Jornada"] = "Indefinido"
    return df

# ============================================================
# SCORES
# ============================================================
def calcular_scores(df):
    # Converter para numérico
    for col in NECESSIDADE_COLS + SUPORTE_COLS + INTENCAO_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    
    # Calcular scores
    df["score_necessidade"] = df[NECESSIDADE_COLS].mean(axis=1)
    df["score_suporte"] = df[SUPORTE_COLS].mean(axis=1) if SUPORTE_COLS else np.nan
    df["score_intencao"] = df[INTENCAO_COLS].mean(axis=1)
    df["score_gap"] = df["score_necessidade"] - df["score_suporte"]
    
    return df

# ============================================================
# LIMPEZA
# ============================================================
def limpar_colunas(df):
    remover = [c for c in df.columns if "Carimbo" in c or "E-MAIL" in c or "Declaro" in c]
    return df.drop(columns=remover, errors="ignore")
