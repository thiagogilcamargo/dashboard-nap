# utils.py
import pandas as pd
import numpy as np
import os

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
    # ============================================================
    # Mapeamento das colunas por palavras-chave (mais robusto)
    # ============================================================
    col_nec1 = None
    col_nec2 = None
    col_nec3 = None
    col_sup = None
    col_int1 = None
    col_int2 = None
    col_int3 = None
    
    for col in df.columns:
        col_lower = col.lower()
        if 'senti necessidade' in col_lower:
            col_nec1 = col
        elif 'confortável' in col_lower and 'procurar ajuda' in col_lower:
            col_nec2 = col
        elif 'acredito que serviços' in col_lower:
            col_nec3 = col
        elif 'suporte suficiente para dificuldades emocionais' in col_lower:
            col_sup = col
        elif 'já pensei em utilizar' in col_lower:
            col_int1 = col
        elif 'confiança na confidencialidade' in col_lower:
            col_int2 = col
        elif 'sei como acessar' in col_lower:
            col_int3 = col
    
    # ============================================================
    # CONVERTER PARA NUMÉRICO
    # ============================================================
    for col in [col_nec1, col_nec2, col_nec3, col_sup, col_int1, col_int2, col_int3]:
        if col:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].fillna(0)
    
    # ============================================================
    # CALCULAR SCORES (com verificações de segurança)
    # ============================================================
    if col_nec1 and col_nec2 and col_nec3:
        df['score_necessidade'] = (df[col_nec1] + df[col_nec2] + df[col_nec3]) / 3
        print(f"✅ Necessidade calculada (média: {df['score_necessidade'].mean():.1f})")
    else:
        print("❌ Colunas de necessidade não encontradas")
        df['score_necessidade'] = 0
    
    if col_sup:
        df['score_suporte'] = df[col_sup]
        print(f"✅ Suporte calculado (média: {df['score_suporte'].mean():.1f})")
    else:
        print("❌ Coluna de suporte não encontrada")
        df['score_suporte'] = 0
    
    if col_int1 and col_int2 and col_int3:
        df['score_intencao'] = (df[col_int1] + df[col_int2] + df[col_int3]) / 3
        print(f"✅ Intenção calculada (média: {df['score_intencao'].mean():.1f})")
    else:
        print("❌ Colunas de intenção não encontradas")
        df['score_intencao'] = 0
    
    # Gap
    df['score_gap'] = df['score_necessidade'] - df['score_suporte']
    
    return df

def calcular_priorizacao(df):
    problemas = []
    
    # Buscar coluna de informação
    col_info = None
    for col in df.columns:
        if 'sei a quem recorrer' in col.lower():
            col_info = col
            break
    
    if col_info:
        df[col_info] = pd.to_numeric(df[col_info], errors='coerce')
        df[col_info] = df[col_info].fillna(0)
        impacto_info = 10 - df[col_info].mean()
        problemas.append({"Problema": "Falta de informação", "Impacto": impacto_info, "Esforço": 2})
    
    # Buscar coluna de preconceito
    col_prec = None
    for col in df.columns:
        if 'preconceito' in col.lower():
            col_prec = col
            break
    
    if col_prec:
        df[col_prec] = pd.to_numeric(df[col_prec], errors='coerce')
        df[col_prec] = df[col_prec].fillna(0)
        impacto_prec = df[col_prec].mean()
        problemas.append({"Problema": "Preconceito", "Impacto": impacto_prec, "Esforço": 6})
    
    if problemas:
        df_problemas = pd.DataFrame(problemas)
        df_problemas['Prioridade'] = df_problemas['Impacto'] / df_problemas['Esforço']
        return df_problemas.sort_values('Prioridade', ascending=False)
    return pd.DataFrame()

def limpar_colunas(df):
    colunas_remover = [col for col in df.columns if 'Carimbo' in col or 'Declaro' in col or 'E-MAIL' in col or 'convidado' in col]
    return df.drop(columns=colunas_remover, errors='ignore')
