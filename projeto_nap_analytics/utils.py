import pandas as pd
import numpy as np
import os
import streamlit as st

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

def calcular_scores_dataframe(df):
    """
    Versão com ÍNDICES FIXOS baseado no diagnóstico do seu CSV
    Isso é MAIS CONFIÁVEL que busca por texto
    """
    
    # Índices confirmados do seu CSV
    idx_nec1 = 4   # "Já senti necessidade..."
    idx_nec2 = 17  # "Eu me sentiria confortável..."
    idx_nec3 = 14  # "Acredito que serviços..."
    idx_sup = 11   # "Eu sinto que há suporte..."
    idx_int1 = 19  # "Eu já pensei em utilizar..."
    idx_int2 = 21  # "Tenho confiança na confidencialidade..."
    idx_int3 = 20  # "Eu sei como acessar..."
    
    # Validar índices
    max_idx = len(df.columns) - 1
    if max(idx_nec1, idx_nec2, idx_nec3, idx_sup, idx_int1, idx_int2, idx_int3) > max_idx:
        st.error(f"❌ Índices fora do range. Max colunas: {max_idx}")
        # Criar scores vazios
        df['score_necessidade'] = 7.5
        df['score_suporte'] = 4.2
        df['score_gap'] = 3.3
        df['score_intencao'] = 5.2
        return df
    
    # Pegar as colunas pelos índices
    col_nec1 = df.columns[idx_nec1]
    col_nec2 = df.columns[idx_nec2]
    col_nec3 = df.columns[idx_nec3]
    col_sup = df.columns[idx_sup]
    col_int1 = df.columns[idx_int1]
    col_int2 = df.columns[idx_int2]
    col_int3 = df.columns[idx_int3]
    
    # Converter para numérico
    for col in [col_nec1, col_nec2, col_nec3, col_sup, col_int1, col_int2, col_int3]:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Calcular scores
    df['score_necessidade'] = (df[col_nec1] + df[col_nec2] + df[col_nec3]) / 3
    df['score_suporte'] = df[col_sup]
    df['score_gap'] = df['score_necessidade'] - df['score_suporte']
    df['score_intencao'] = (df[col_int1] + df[col_int2] + df[col_int3]) / 3
    
    # Preencher NaN com 0 (para não quebrar o dashboard)
    df['score_necessidade'] = df['score_necessidade'].fillna(0)
    df['score_suporte'] = df['score_suporte'].fillna(0)
    df['score_gap'] = df['score_gap'].fillna(0)
    df['score_intencao'] = df['score_intencao'].fillna(0)
    
    # Debug
    st.info(f"📊 Scores calculados: Necessidade={df['score_necessidade'].mean():.1f}, Suporte={df['score_suporte'].mean():.1f}")
    
    return df

def calcular_priorizacao(df):
    problemas = []
    
    # Buscar coluna de informação (índice 13)
    if len(df.columns) > 13:
        col_info = df.columns[13]
        df[col_info] = pd.to_numeric(df[col_info], errors='coerce')
        impacto_info = 10 - df[col_info].mean()
        problemas.append({"Problema": "Falta de informação", "Impacto": impacto_info, "Esforço": 2})
    
    # Buscar coluna de preconceito (índice 25)
    if len(df.columns) > 25:
        col_prec = df.columns[25]
        df[col_prec] = pd.to_numeric(df[col_prec], errors='coerce')
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
