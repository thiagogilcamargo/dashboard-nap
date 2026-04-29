# utils.py
import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_RAW = os.path.join(BASE_DIR, "dados", "raw", "dados.csv")

def carregar_dados_brutos():
    df = pd.read_csv(PATH_RAW, encoding='utf-8-sig')
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
    # USANDO ÍNDICES DIRETOS DAS COLUNAS
    # Com base na sua listagem: 
    # índice 10 = Necessidade 1
    # índice 19 = Conforto (Necessidade 2)
    # índice 16 = Acredita (Necessidade 3)
    # índice 13 = Suporte
    # índice 21, 22, 23 = Intenção
    
    # Converter para numérico usando iloc (posição, não nome)
    for i in [10, 13, 16, 19, 21, 22, 23]:
        if i < len(df.columns):
            df.iloc[:, i] = pd.to_numeric(df.iloc[:, i], errors='coerce')
    
    # Necessidade = média das colunas 10, 19, 16
    df['score_necessidade'] = (
        df.iloc[:, 10] + df.iloc[:, 19] + df.iloc[:, 16]
    ) / 3
    
    # Suporte = coluna 13
    df['score_suporte'] = df.iloc[:, 13]
    
    # Gap
    df['score_gap'] = df['score_necessidade'] - df['score_suporte']
    
    # Intenção = média das colunas 21, 22, 23
    df['score_intencao'] = (
        df.iloc[:, 21] + df.iloc[:, 22] + df.iloc[:, 23]
    ) / 3
    
    print(f"✅ Necessidade média: {df['score_necessidade'].mean():.1f}")
    print(f"✅ Suporte média: {df['score_suporte'].mean():.1f}")
    print(f"✅ Gap média: {df['score_gap'].mean():.1f}")
    
    return df

def calcular_priorizacao(df):
    problemas = []
    
    # coluna 15 = "Eu sei a quem recorrer..."
    if 15 < len(df.columns):
        col_data = pd.to_numeric(df.iloc[:, 15], errors='coerce')
        impacto_info = 10 - col_data.mean()
        problemas.append({"Problema": "Falta de informação", "Impacto": impacto_info, "Esforço": 2})
    
    # coluna 25 = "Sinto que existe preconceito..."
    if 25 < len(df.columns):
        col_data = pd.to_numeric(df.iloc[:, 25], errors='coerce')
        impacto_prec = col_data.mean()
        problemas.append({"Problema": "Preconceito", "Impacto": impacto_prec, "Esforço": 6})
    
    if problemas:
        df_problemas = pd.DataFrame(problemas)
        if df_problemas['Impacto'].max() != df_problemas['Impacto'].min():
            df_problemas['Impacto_norm'] = (df_problemas['Impacto'] - df_problemas['Impacto'].min()) / (df_problemas['Impacto'].max() - df_problemas['Impacto'].min())
        else:
            df_problemas['Impacto_norm'] = 0
        df_problemas['Esforço_norm'] = (df_problemas['Esforço'] - df_problemas['Esforço'].min()) / (df_problemas['Esforço'].max() - df_problemas['Esforço'].min())
        df_problemas['Prioridade'] = df_problemas['Impacto_norm'] * (1 - df_problemas['Esforço_norm'])
        return df_problemas.sort_values('Prioridade', ascending=False)
    
    return pd.DataFrame()

def limpar_colunas(df):
    colunas_remover = [col for col in df.columns if 'Carimbo' in col or 'Declaro' in col or 'E-MAIL' in col or 'convidado' in col]
    return df.drop(columns=colunas_remover, errors='ignore')
