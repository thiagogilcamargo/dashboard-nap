# utils.py
import pandas as pd
import numpy as np
import os
from config.config import PATH_RAW, JORNADA_COL

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
    if JORNADA_COL in df.columns:
        df['Jornada'] = df[JORNADA_COL].apply(classificar_jornada)
    else:
        df['Jornada'] = "Indefinido"
    return df

def calcular_scores(df):
    cols_perc = [
        "Já senti necessidade de apoio emocional durante a graduação.",
        "Eu me sentiria confortável em procurar ajuda dentro da instituição.",
        "Eu sinto que há suporte suficiente para dificuldades emocionais na faculdade.",
        "Acredito que serviços de apoio podem melhorar a experiência acadêmica dos alunos."
    ]
    
    for col in cols_perc:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df['score_necessidade'] = df[cols_perc[:3]].mean(axis=1) if len(cols_perc) >= 3 else np.nan
    df['score_suporte'] = df[cols_perc[2]] if len(cols_perc) > 2 else np.nan
    df['score_gap'] = df['score_necessidade'] - df['score_suporte'] if 'score_necessidade' in df.columns and 'score_suporte' in df.columns else np.nan
    
    cols_int = [
        "Eu já pensei em utilizar o NAP (Núcleo de Apoio Psicopedagógico) em algum momento.",
        "Tenho confiança na confidencialidade do atendimento oferecido pelo NAP (Núcleo de Apoio Psicopedagógico).",
        "Eu sei como acessar os serviços oferecidos pelo NAP  (Núcleo de Apoio Psicopedagógico)."
    ]
    for col in cols_int:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    df['score_intencao'] = df[cols_int].mean(axis=1)
    
    return df

def limpar_colunas(df):
    remover = [col for col in df.columns if 'Carimbo' in col or 'Declaro' in col or 'E-MAIL' in col or 'convidado' in col]
    return df.drop(columns=remover, errors='ignore')
