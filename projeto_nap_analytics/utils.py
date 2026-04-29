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
    # MÉTODO 1: Tentar encontrar pelos NOMES
    # ============================================================
    col_nec1 = "Já senti necessidade de apoio emocional durante a graduação."
    col_nec2 = "Eu me sentiria confortável em procurar ajuda dentro da instituição."
    col_nec3 = "Acredito que serviços de apoio podem melhorar a experiência acadêmica dos alunos."
    col_sup = "Eu sinto que há suporte suficiente para dificuldades emocionais na faculdade."
    
    # Verificar se os nomes existem
    nec1_existe = col_nec1 in df.columns
    nec2_existe = col_nec2 in df.columns
    nec3_existe = col_nec3 in df.columns
    sup_existe = col_sup in df.columns
    
    # ============================================================
    # MÉTODO 2: Se não encontrar pelos nomes, usar índices conhecidos
    # ============================================================
    if not (nec1_existe and nec2_existe and nec3_existe and sup_existe):
        print("⚠️ Colunas não encontradas pelos nomes. Usando índices...")
        # Baseado no diagnóstico:
        # Índice 4: "Já senti necessidade..." (antes do range 10-19)
        # Índice 17: "Eu me sentiria confortável..."
        # Índice 14: "Acredito que serviços..."
        # Índice 11: "Eu sinto que há suporte..."
        
        # Encontrar dinamicamente: procurar palavras-chave
        for i, col in enumerate(df.columns):
            if 'senti necessidade' in col.lower():
                col_nec1 = col
                nec1_existe = True
            if 'confortável' in col.lower():
                col_nec2 = col
                nec2_existe = True
            if 'acredito que serviços' in col.lower():
                col_nec3 = col
                nec3_existe = True
            if 'suporte suficiente para dificuldades emocionais' in col.lower():
                col_sup = col
                sup_existe = True
    
    # ============================================================
    # CONVERTER PARA NUMÉRICO E CALCULAR
    # ============================================================
    if nec1_existe and nec2_existe and nec3_existe and sup_existe:
        # Converter para numérico
        for col in [col_nec1, col_nec2, col_nec3, col_sup]:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].fillna(0)
        
        df['score_necessidade'] = (df[col_nec1] + df[col_nec2] + df[col_nec3]) / 3
        df['score_suporte'] = df[col_sup]
        df['score_gap'] = df['score_necessidade'] - df['score_suporte']
        
        print(f"✅ Necessidade média: {df['score_necessidade'].mean():.1f}")
        print(f"✅ Suporte média: {df['score_suporte'].mean():.1f}")
    else:
        print("❌ Não foi possível encontrar as colunas necessárias")
        df['score_necessidade'] = 0
        df['score_suporte'] = 0
        df['score_gap'] = 0
    
    # ============================================================
    # INTENÇÃO (já funcionava)
    # ============================================================
    col_int1 = "Eu já pensei em utilizar o NAP (Núcleo de Apoio Psicopedagógico) em algum momento."
    col_int2 = "Tenho confiança na confidencialidade do atendimento oferecido pelo NAP (Núcleo de Apoio Psicopedagógico)."
    col_int3 = "Eu sei como acessar os serviços oferecidos pelo NAP  (Núcleo de Apoio Psicopedagógico)."
    
    for col in [col_int1, col_int2, col_int3]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].fillna(0)
    
    df['score_intencao'] = (df[col_int1] + df[col_int2] + df[col_int3]) / 3
    
    return df

def calcular_priorizacao(df):
    problemas = []
    col_info = "Eu sei a quem recorrer dentro da faculdade quando tenho dificuldades emocionais."
    if col_info in df.columns:
        df[col_info] = pd.to_numeric(df[col_info], errors='coerce')
        df[col_info] = df[col_info].fillna(0)
        impacto_info = 10 - df[col_info].mean()
        problemas.append({"Problema": "Falta de informação", "Impacto": impacto_info, "Esforço": 2})
    
    col_prec = "Sinto que existe um preconceito em procurar apoio psicológico ou pedagógico na instituição."
    if col_prec in df.columns:
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
