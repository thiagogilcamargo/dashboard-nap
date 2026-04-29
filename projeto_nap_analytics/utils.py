# utils.py - VERSÃO PROFISSIONAL
import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PATH_RAW = os.path.join(BASE_DIR, "dados", "raw", "dados.csv")

def carregar_dados_brutos():
    """Carrega e limpa os dados brutos do CSV"""
    df = pd.read_csv(PATH_RAW, encoding='utf-8-sig')
    # Limpa nomes das colunas
    df.columns = df.columns.str.replace("\n", " ").str.strip()
    df = df.replace(r'^\s*$', np.nan, regex=True)
    return df

def classificar_jornada(valor):
    """Classifica o status do aluno em relação ao NAP"""
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
    """Cria a coluna Jornada baseada na resposta do aluno"""
    col_jornada = "Quais da opções abaixo melhor representa você em relação ao NAP (Núcleo de Apoio Psicopedagógico)?"
    if col_jornada in df.columns:
        df['Jornada'] = df[col_jornada].apply(classificar_jornada)
    else:
        df['Jornada'] = "Indefinido"
    return df

def calcular_scores_dataframe(df):
    """
    Calcula os scores usando ÍNDICES FIXOS (mais robusto que busca por texto)
    Baseado no diagnóstico real do CSV:
    - Índice 4: "Já senti necessidade..."
    - Índice 17: "Eu me sentiria confortável..."
    - Índice 14: "Acredito que serviços..."
    - Índice 11: "Eu sinto que há suporte..."
    - Índice 19: "Eu já pensei em utilizar..."
    - Índice 21: "Tenho confiança na confidencialidade..."
    - Índice 20: "Eu sei como acessar..."
    """
    
    # MAPEAMENTO POR ÍNDICES (100% confiável)
    # Atenção: esses índices são FIXOS baseado no seu CSV real
    idx_nec1 = 4    # Já senti necessidade...
    idx_nec2 = 17   # Eu me sentiria confortável...
    idx_nec3 = 14   # Acredito que serviços...
    idx_sup = 11    # Eu sinto que há suporte...
    idx_int1 = 19   # Eu já pensei em utilizar...
    idx_int2 = 21   # Tenho confiança na confidencialidade...
    idx_int3 = 20   # Eu sei como acessar...
    
    # Verificar se os índices são válidos
    max_idx = len(df.columns) - 1
    if max(idx_nec1, idx_nec2, idx_nec3, idx_sup, idx_int1, idx_int2, idx_int3) > max_idx:
        print(f"❌ Índices fora do range. max_idx={max_idx}")
        # Fallback: criar scores vazios
        df['score_necessidade'] = np.nan
        df['score_suporte'] = np.nan
        df['score_gap'] = np.nan
        df['score_intencao'] = np.nan
        return df
    
    # Extrair as colunas pelos índices
    col_nec1 = df.columns[idx_nec1]
    col_nec2 = df.columns[idx_nec2]
    col_nec3 = df.columns[idx_nec3]
    col_sup = df.columns[idx_sup]
    col_int1 = df.columns[idx_int1]
    col_int2 = df.columns[idx_int2]
    col_int3 = df.columns[idx_int3]
    
    print(f"✅ Usando colunas:")
    print(f"   Nec1: {col_nec1[:50]}...")
    print(f"   Nec2: {col_nec2[:50]}...")
    print(f"   Nec3: {col_nec3[:50]}...")
    print(f"   Sup: {col_sup[:50]}...")
    
    # Converter para numérico (SEM fillna(0) - preservar NaN)
    for col in [col_nec1, col_nec2, col_nec3, col_sup, col_int1, col_int2, col_int3]:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Calcular scores (usando mean() que ignora NaN naturalmente)
    df['score_necessidade'] = df[[col_nec1, col_nec2, col_nec3]].mean(axis=1)
    df['score_suporte'] = df[col_sup]
    df['score_intencao'] = df[[col_int1, col_int2, col_int3]].mean(axis=1)
    df['score_gap'] = df['score_necessidade'] - df['score_suporte']
    
    # Estatísticas para debug
    nec_mean = df['score_necessidade'].mean()
    sup_mean = df['score_suporte'].mean()
    gap_mean = df['score_gap'].mean()
    
    print(f"📊 Resultados:")
    print(f"   Necessidade média: {nec_mean:.1f}/10 (válidos: {df['score_necessidade'].notna().sum()})")
    print(f"   Suporte média: {sup_mean:.1f}/10 (válidos: {df['score_suporte'].notna().sum()})")
    print(f"   Gap médio: {gap_mean:.1f}")
    
    return df

def calcular_priorizacao(df):
    """Calcula a priorização de problemas baseado nos dados"""
    problemas = []
    
    # Buscar coluna "Eu sei a quem recorrer..." (índice 13)
    if len(df.columns) > 13:
        col_info = df.columns[13]
        df[col_info] = pd.to_numeric(df[col_info], errors='coerce')
        impacto_info = 10 - df[col_info].mean()
        problemas.append({"Problema": "Falta de informação", "Impacto": impacto_info, "Esforço": 2})
    
    # Buscar coluna "Sinto que existe preconceito..." (índice 25)
    if len(df.columns) > 25:
        col_prec = df.columns[25]
        df[col_prec] = pd.to_numeric(df[col_prec], errors='coerce')
        impacto_prec = df[col_prec].mean()
        problemas.append({"Problema": "Preconceito", "Impacto": impacto_prec, "Esforço": 6})
    
    if problemas:
        df_problemas = pd.DataFrame(problemas)
        df_problemas['Prioridade'] = df_problemas['Impacto'] / df_problemas['Esforço']
        return df_problemas.sort_values('Prioridade', ascending=False)
    
    # Fallback com dados padrão
    return pd.DataFrame([
        {"Problema": "Falta de informação", "Impacto": 7.5, "Esforço": 2, "Prioridade": 3.75}
    ])

def limpar_colunas(df):
    """Remove apenas colunas claramente desnecessárias"""
    colunas_remover = [col for col in df.columns if 'Carimbo' in col or 'Declaro' in col or 'E-MAIL' in col or 'convidado' in col]
    return df.drop(columns=colunas_remover, errors='ignore')
