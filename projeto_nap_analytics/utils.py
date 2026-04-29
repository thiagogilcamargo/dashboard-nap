# utils.py - VERSÃO PROFISSIONAL (SEM ÍNDICES FIXOS)
import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PATH_RAW = os.path.join(BASE_DIR, "dados", "raw", "dados.csv")

def carregar_dados_brutos():
    """Carrega e limpa os dados brutos do CSV"""
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

def encontrar_coluna_por_palavras_chave(df, palavras):
    """
    Encontra uma coluna no DataFrame que contenha TODAS as palavras-chave
    Retorna o nome da coluna ou None se não encontrar
    """
    for col in df.columns:
        col_lower = col.lower()
        if all(palavra.lower() in col_lower for palavra in palavras):
            return col
    return None

def validar_coluna(df, col_nome, contexto):
    """
    Valida se uma coluna existe e tem dados válidos
    Retorna (existe, percentual_valido)
    """
    if col_nome is None or col_nome not in df.columns:
        return False, 0
    
    dados_validos = pd.to_numeric(df[col_nome], errors='coerce').notna().sum()
    percentual = (dados_validos / len(df)) * 100
    return True, percentual

def calcular_scores_dataframe(df):
    """
    Calcula os scores usando busca por NOMES (não índices fixos)
    Tolerante a NaN: usa skipna=True e fillna com a média da coluna
    """
    
    # ============================================================
    # 1. Encontrar as colunas pelos NOMES (robusto)
    # ============================================================
    col_nec1 = encontrar_coluna_por_palavras_chave(df, ["senti", "necessidade", "emocional"])
    col_nec2 = encontrar_coluna_por_palavras_chave(df, ["confortável", "procurar", "ajuda"])
    col_nec3 = encontrar_coluna_por_palavras_chave(df, ["acredito", "serviços", "apoio", "melhorar"])
    col_sup = encontrar_coluna_por_palavras_chave(df, ["suporte", "suficiente", "emocionais"])
    
    col_int1 = encontrar_coluna_por_palavras_chave(df, ["pensei", "utilizar", "NAP"])
    col_int2 = encontrar_coluna_por_palavras_chave(df, ["confiança", "confidencialidade"])
    col_int3 = encontrar_coluna_por_palavras_chave(df, ["acessar", "serviços", "oferecidos"])
    
    # ============================================================
    # 2. Validar e reportar
    # ============================================================
    print("=" * 50)
    print("🔍 VALIDAÇÃO DAS COLUNAS")
    print("=" * 50)
    
    for nome, col in [("Nec1", col_nec1), ("Nec2", col_nec2), ("Nec3", col_nec3), 
                      ("Sup", col_sup), ("Int1", col_int1), ("Int2", col_int2), ("Int3", col_int3)]:
        existe, pct = validar_coluna(df, col, nome)
        if existe:
            print(f"✅ {nome}: '{col[:40]}...' ({pct:.1f}% válidos)")
        else:
            print(f"❌ {nome}: NÃO ENCONTRADA")
    
    # ============================================================
    # 3. Converter para numérico (sem fillna ainda)
    # ============================================================
    for col in [col_nec1, col_nec2, col_nec3, col_sup, col_int1, col_int2, col_int3]:
        if col:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # ============================================================
    # 4. Calcular Necessidade (média ignorando NaN)
    # ============================================================
    if col_nec1 and col_nec2 and col_nec3:
        df['score_necessidade'] = df[[col_nec1, col_nec2, col_nec3]].mean(axis=1, skipna=True)
        # Preencher NaN com a média da coluna (melhor que 0)
        media_nec = df['score_necessidade'].mean()
        df['score_necessidade'] = df['score_necessidade'].fillna(media_nec)
        print(f"📊 Necessidade: média {df['score_necessidade'].mean():.1f}/10")
    else:
        print("❌ Necessidade: colunas insuficientes")
        df['score_necessidade'] = np.nan
    
    # ============================================================
    # 5. Calcular Suporte
    # ============================================================
    if col_sup:
        df['score_suporte'] = df[col_sup]
        media_sup = df['score_suporte'].mean()
        df['score_suporte'] = df['score_suporte'].fillna(media_sup)
        print(f"📊 Suporte: média {df['score_suporte'].mean():.1f}/10")
    else:
        print("❌ Suporte: coluna não encontrada")
        df['score_suporte'] = np.nan
    
    # ============================================================
    # 6. Calcular Gap
    # ============================================================
    if 'score_necessidade' in df.columns and 'score_suporte' in df.columns:
        df['score_gap'] = df['score_necessidade'] - df['score_suporte']
        print(f"📊 Gap médio: {df['score_gap'].mean():.1f}")
    
    # ============================================================
    # 7. Calcular Intenção
    # ============================================================
    if col_int1 and col_int2 and col_int3:
        df['score_intencao'] = df[[col_int1, col_int2, col_int3]].mean(axis=1, skipna=True)
        media_int = df['score_intencao'].mean()
        df['score_intencao'] = df['score_intencao'].fillna(media_int)
        print(f"📊 Intenção: média {df['score_intencao'].mean():.1f}/10")
    else:
        print("❌ Intenção: colunas insuficientes")
        df['score_intencao'] = np.nan
    
    print("=" * 50)
    
    return df

def calcular_priorizacao(df):
    """Calcula priorização com busca por nome"""
    problemas = []
    
    col_info = encontrar_coluna_por_palavras_chave(df, ["sei", "recorrer", "dificuldades", "emocionais"])
    if col_info:
        df[col_info] = pd.to_numeric(df[col_info], errors='coerce')
        impacto_info = 10 - df[col_info].mean()
        problemas.append({"Problema": "Falta de informação", "Impacto": impacto_info, "Esforço": 2})
    
    col_prec = encontrar_coluna_por_palavras_chave(df, ["preconceito", "procurar", "apoio"])
    if col_prec:
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
