# utils.py
import pandas as pd
import numpy as np
import os
import streamlit as st
from difflib import get_close_matches

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
        # Fallback: buscar por palavra-chave
        for col in df.columns:
            if 'nap' in col.lower() and ('conheço' in col.lower() or 'representa' in col.lower()):
                df['Jornada'] = df[col].apply(classificar_jornada)
                break
        else:
            df['Jornada'] = "Indefinido"
    return df

# ============================================================
# MAPEAMENTO SEMÂNTICO (100% - SEM ÍNDICES FIXOS)
# ============================================================

def normalizar_string(texto: str) -> str:
    if not isinstance(texto, str):
        return ""
    texto = texto.lower()
    texto = texto.replace("ã", "a").replace("õ", "o").replace("á", "a")
    texto = texto.replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    texto = texto.replace("ç", "c")
    texto = ''.join(c for c in texto if c.isalnum() or c.isspace())
    return texto.strip()

def encontrar_coluna(df, nome_esperado: str, palavras_chave: list) -> str:
    """Encontra coluna por nome exato, palavras-chave ou fuzzy matching"""
    nome_norm = normalizar_string(nome_esperado)
    
    for col in df.columns:
        if col == nome_esperado:
            return col
    
    for col in df.columns:
        col_norm = normalizar_string(col)
        for palavra in palavras_chave:
            if normalizar_string(palavra) in col_norm:
                return col
    
    colunas_norm = {col: normalizar_string(col) for col in df.columns}
    matches = get_close_matches(nome_norm, list(colunas_norm.values()), n=1, cutoff=0.7)
    if matches:
        for col, col_norm in colunas_norm.items():
            if col_norm == matches[0]:
                return col
    
    return None

# ============================================================
# CAMADA DE QUALIDADE DE DADOS (Data Quality Panel)
# ============================================================

def relatorio_qualidade_dados(df):
    """Gera relatório de qualidade por coluna de score"""
    colunas_score = [
        "Já senti necessidade de apoio emocional durante a graduação.",
        "Eu me sentiria confortável em procurar ajuda dentro da instituição.",
        "Acredito que serviços de apoio podem melhorar a experiência acadêmica dos alunos.",
        "Eu sinto que há suporte suficiente para dificuldades emocionais na faculdade.",
        "Eu já pensei em utilizar o NAP (Núcleo de Apoio Psicopedagógico) em algum momento.",
        "Tenho confiança na confidencialidade do atendimento oferecido pelo NAP (Núcleo de Apoio Psicopedagógico).",
        "Eu sei como acessar os serviços oferecidos pelo NAP (Núcleo de Apoio Psicopedagógico)."
    ]
    
    qualidade = {}
    for col in colunas_score:
        if col in df.columns:
            validos = df[col].notna().sum()
            qualidade[col] = {
                "valido": validos,
                "total": len(df),
                "percentual": (validos / len(df)) * 100,
                "tipo": df[col].dtype
            }
        else:
            qualidade[col] = {
                "valido": 0,
                "total": len(df),
                "percentual": 0,
                "tipo": "coluna_ausente"
            }
    
    return qualidade

def mediana_historica(df, coluna):
    """Calcula mediana histórica para fallback inteligente"""
    dados_validos = df[coluna].dropna()
    if len(dados_validos) > 10:
        return dados_validos.median()
    return None

# ============================================================
# SCORE COM CONFIANÇA (SEM fillna(0))
# ============================================================

def calcular_score_com_confianca(df, colunas, nome_score, min_respostas=2):
    validas = df[colunas].notna().sum(axis=1)
    media = df[colunas].mean(axis=1, skipna=True)
    score = media.where(validas >= min_respostas, np.nan)
    confianca = (validas / len(colunas)).round(2)
    return score, confianca

def calcular_scores_dataframe(df):
    """Versão 100% semântica - SEM ÍNDICES FIXOS"""
    
    # Mapeamento das colunas
    col_nec1 = encontrar_coluna(df, 
        "Já senti necessidade de apoio emocional durante a graduação.",
        ["necessidade", "apoio emocional", "senti necessidade"])
    
    col_nec2 = encontrar_coluna(df,
        "Eu me sentiria confortável em procurar ajuda dentro da instituição.",
        ["confortável", "procurar ajuda", "confortavel"])
    
    col_nec3 = encontrar_coluna(df,
        "Acredito que serviços de apoio podem melhorar a experiência acadêmica dos alunos.",
        ["acredito", "serviços", "melhorar", "experiência acadêmica"])
    
    col_sup = encontrar_coluna(df,
        "Eu sinto que há suporte suficiente para dificuldades emocionais na faculdade.",
        ["suporte", "suficiente", "dificuldades emocionais"])
    
    col_int1 = encontrar_coluna(df,
        "Eu já pensei em utilizar o NAP (Núcleo de Apoio Psicopedagógico) em algum momento.",
        ["pensei", "utilizar", "NAP"])
    
    col_int2 = encontrar_coluna(df,
        "Tenho confiança na confidencialidade do atendimento oferecido pelo NAP (Núcleo de Apoio Psicopedagógico).",
        ["confiança", "confidencialidade"])
    
    col_int3 = encontrar_coluna(df,
        "Eu sei como acessar os serviços oferecidos pelo NAP (Núcleo de Apoio Psicopedagógico).",
        ["acessar", "serviços", "oferecidos"])
    
    # Relatório de qualidade (debug)
    colunas_necessidade = [c for c in [col_nec1, col_nec2, col_nec3] if c]
    colunas_intencao = [c for c in [col_int1, col_int2, col_int3] if c]
    
    st.info(f"🔍 Mapeamento: Necessidade={len(colunas_necessidade)}/3, Suporte={'✅' if col_sup else '❌'}, Intenção={len(colunas_intencao)}/3")
    
    # Converter para numérico
    for col in colunas_necessidade + [col_sup] + colunas_intencao:
        if col:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Score Necessidade
    if len(colunas_necessidade) >= 2:
        df['score_necessidade'], df['score_necessidade_confianca'] = calcular_score_com_confianca(
            df, colunas_necessidade, "necessidade", min_respostas=2
        )
    else:
        df['score_necessidade'] = np.nan
        df['score_necessidade_confianca'] = 0
    
    # Score Suporte
    if col_sup:
        df['score_suporte'] = df[col_sup]
        df['score_suporte_confianca'] = df[col_sup].notna().astype(float)
    else:
        df['score_suporte'] = np.nan
        df['score_suporte_confianca'] = 0
    
    # Score Intenção
    if len(colunas_intencao) >= 2:
        df['score_intencao'], df['score_intencao_confianca'] = calcular_score_com_confianca(
            df, colunas_intencao, "intencao", min_respostas=2
        )
    else:
        df['score_intencao'] = np.nan
        df['score_intencao_confianca'] = 0
    
    # Gap
    df['score_gap'] = df['score_necessidade'] - df['score_suporte']
    df['score_gap_confianca'] = df[['score_necessidade_confianca', 'score_suporte_confianca']].min(axis=1)
    
    return df

def calcular_priorizacao(df):
    problemas = []
    
    col_info = encontrar_coluna(df,
        "Eu sei a quem recorrer dentro da faculdade quando tenho dificuldades emocionais.",
        ["sei a quem recorrer", "dificuldades emocionais"])
    
    if col_info:
        dados = pd.to_numeric(df[col_info], errors='coerce').dropna()
        if len(dados) > 10:
            impacto_info = 10 - dados.mean()
            problemas.append({"Problema": "Falta de informação", "Impacto": impacto_info, "Esforço": 2, "n_amostras": len(dados)})
    
    col_prec = encontrar_coluna(df,
        "Sinto que existe um preconceito em procurar apoio psicológico ou pedagógico na instituição.",
        ["preconceito", "procurar apoio"])
    
    if col_prec:
        dados = pd.to_numeric(df[col_prec], errors='coerce').dropna()
        if len(dados) > 10:
            impacto_prec = dados.mean()
            problemas.append({"Problema": "Preconceito", "Impacto": impacto_prec, "Esforço": 6, "n_amostras": len(dados)})
    
    if problemas:
        df_problemas = pd.DataFrame(problemas)
        df_problemas['Prioridade'] = df_problemas['Impacto'] / df_problemas['Esforço']
        return df_problemas.sort_values('Prioridade', ascending=False)
    
    return pd.DataFrame()

def limpar_colunas(df):
    colunas_remover = [col for col in df.columns if 'Carimbo' in col or 'Declaro' in col or 'E-MAIL' in col or 'convidado' in col]
    return df.drop(columns=colunas_remover, errors='ignore')
