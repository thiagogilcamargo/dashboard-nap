# utils.py
import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_RAW = os.path.join(BASE_DIR, "dados", "raw", "dados.csv")

def carregar_dados_brutos():
    df = pd.read_csv(PATH_RAW, encoding='utf-8')
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
    # Busca as colunas pelo nome (flexível)
    def encontra_coluna(palavras_chave):
        for col in df.columns:
            if all(p in col for p in palavras_chave):
                return col
        return None
    
    # Necessidade (média de 3 perguntas)
    col_necessidade1 = encontra_coluna(["necessidade", "apoio emocional"])
    col_necessidade2 = encontra_coluna(["confortável", "procurar ajuda"])
    col_necessidade3 = encontra_coluna(["acredito", "serviços", "apoio", "melhorar"])
    
    # Suporte (1 pergunta)
    col_suporte = encontra_coluna(["sinto", "suporte suficiente", "emocionais"])
    
    # Intenção (3 perguntas - adaptado)
    col_intencao1 = encontra_coluna(["pensei", "utilizar", "NAP"])
    col_intencao2 = encontra_coluna(["confiança", "confidencialidade"])
    col_intencao3 = encontra_coluna["sei como acessar"]
    
    # Converte para numérico e calcula
    if col_necessidade1 and col_necessidade2 and col_necessidade3:
        df[col_necessidade1] = pd.to_numeric(df[col_necessidade1], errors='coerce')
        df[col_necessidade2] = pd.to_numeric(df[col_necessidade2], errors='coerce')
        df[col_necessidade3] = pd.to_numeric(df[col_necessidade3], errors='coerce')
        df['score_necessidade'] = df[[col_necessidade1, col_necessidade2, col_necessidade3]].mean(axis=1)
    
    if col_suporte:
        df[col_suporte] = pd.to_numeric(df[col_suporte], errors='coerce')
        df['score_suporte'] = df[col_suporte]
    
    if 'score_necessidade' in df.columns and 'score_suporte' in df.columns:
        df['score_gap'] = df['score_necessidade'] - df['score_suporte']
    
    return df

def limpar_colunas(df):
    colunas_remover = [col for col in df.columns if 'Carimbo' in col or 'Declaro' in col or 'E-MAIL' in col or 'convidado' in col]
    return df.drop(columns=colunas_remover, errors='ignore')
