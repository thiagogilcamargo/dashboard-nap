# scripts/02_scores.py
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import (
    PATH_PROCESSED, 
    PERCEPCAO_COLS, 
    INTENCAO_COLS, 
    EXPERIENCIA_COLS, 
    ACESSO_COLS
)

def calcular_scores(df):
    cols_numericas = PERCEPCAO_COLS + INTENCAO_COLS + EXPERIENCIA_COLS + ACESSO_COLS
    for col in cols_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df['score_percepcao'] = df[PERCEPCAO_COLS].mean(axis=1)
    df['score_intencao'] = df[INTENCAO_COLS].mean(axis=1)
    df['score_experiencia'] = df[EXPERIENCIA_COLS].mean(axis=1)
    df['score_acesso'] = df[ACESSO_COLS].mean(axis=1)
    
    return df

def run_scores():
    print("📊 Carregando dados modelados...")
    df = pd.read_csv(PATH_PROCESSED)
    
    print("📐 Calculando scores por dimensão...")
    df = calcular_scores(df)
    
    print(f"💾 Salvando dados com scores em {PATH_PROCESSED}")
    df.to_csv(PATH_PROCESSED, index=False)
    print("✅ Scores calculados com sucesso.")

if __name__ == "__main__":
    run_scores()