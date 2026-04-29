# projeto_nap_analytics/utils.py
import sys
import os
import pandas as pd
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import (
    PATH_RAW, 
    PERCEPCAO_COLS, 
    INTENCAO_COLS, 
    EXPERIENCIA_COLS, 
    ACESSO_COLS, 
    JORNADA_COL,
    ESFORCO_PROBLEMAS
)

def carregar_dados_brutos():
    df = pd.read_csv(PATH_RAW, encoding='utf-8')
    df = df.replace(r'^\s*$', np.nan, regex=True)
    return df

def classificar_jornada(valor):
    """3 status corretos do NAP"""
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

def calcular_scores_dataframe(df):
    todas_colunas = PERCEPCAO_COLS + INTENCAO_COLS + EXPERIENCIA_COLS + ACESSO_COLS
    for col in todas_colunas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    percepcao_exist = [c for c in PERCEPCAO_COLS if c in df.columns]
    if percepcao_exist:
        df['score_percepcao'] = df[percepcao_exist].mean(axis=1)
    
    intencao_exist = [c for c in INTENCAO_COLS if c in df.columns]
    if intencao_exist:
        df['score_intencao'] = df[intencao_exist].mean(axis=1)
    
    experiencia_exist = [c for c in EXPERIENCIA_COLS if c in df.columns]
    if experiencia_exist:
        df['score_experiencia'] = df[experiencia_exist].mean(axis=1)
    
    acesso_exist = [c for c in ACESSO_COLS if c in df.columns]
    if acesso_exist:
        df['score_acesso'] = df[acesso_exist].mean(axis=1)
    
    return df

def calcular_priorizacao(df):
    problemas = []
    
    col_info = "Eu sei a quem recorrer dentro da faculdade quando tenho dificuldades emocionais."
    if col_info in df.columns:
        impacto_info = 10 - df[col_info].mean()
        problemas.append({"Problema": "Falta de informação", "Impacto": impacto_info})
    
    col_prec = "Sinto que existe um preconceito em procurar apoio psicológico ou pedagógico na instituição."
    if col_prec in df.columns:
        df[col_prec] = pd.to_numeric(df[col_prec], errors='coerce')
        impacto_prec = df[col_prec].mean()
        problemas.append({"Problema": "Preconceito", "Impacto": impacto_prec})
    
    col_acesso = "Considero o NAP (Núcleo de Apoio Psicopedagógico) acessível em termos de horário e localização."
    if col_acesso in df.columns:
        df[col_acesso] = pd.to_numeric(df[col_acesso], errors='coerce')
        impacto_acesso = 10 - df[col_acesso].dropna().mean()
        problemas.append({"Problema": "Acesso (horários/local)", "Impacto": impacto_acesso})
    
    col_espera = "O tempo de espera para atendimento foi adequado."
    if col_espera in df.columns:
        df[col_espera] = pd.to_numeric(df[col_espera], errors='coerce')
        impacto_espera = 10 - df[col_espera].dropna().mean()
        problemas.append({"Problema": "Tempo de espera", "Impacto": impacto_espera})
    
    df_problemas = pd.DataFrame(problemas)
    if not df_problemas.empty:
        df_problemas['Esforço'] = df_problemas['Problema'].map(ESFORCO_PROBLEMAS)
        
        if df_problemas['Impacto'].max() != df_problemas['Impacto'].min():
            df_problemas['Impacto_norm'] = (df_problemas['Impacto'] - df_problemas['Impacto'].min()) / (df_problemas['Impacto'].max() - df_problemas['Impacto'].min())
        else:
            df_problemas['Impacto_norm'] = 0
            
        if df_problemas['Esforço'].max() != df_problemas['Esforço'].min():
            df_problemas['Esforço_norm'] = (df_problemas['Esforço'] - df_problemas['Esforço'].min()) / (df_problemas['Esforço'].max() - df_problemas['Esforço'].min())
        else:
            df_problemas['Esforço_norm'] = 0
            
        df_problemas['Prioridade'] = df_problemas['Impacto_norm'] * (1 - df_problemas['Esforço_norm'])
        df_problemas = df_problemas.sort_values('Prioridade', ascending=False)
    
    return df_problemas

def limpar_colunas(df):
    colunas_remover = [col for col in df.columns if 'Carimbo' in col or 'Declaro' in col or 'E-MAIL' in col or 'convidado' in col]
    return df.drop(columns=colunas_remover, errors='ignore')
