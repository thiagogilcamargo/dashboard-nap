# utils.py - VERSÃO FINAL CORRIGIDA
import pandas as pd
import numpy as np
import os

# CORREÇÃO 1: BASE_DIR correto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PATH_RAW = os.path.join(BASE_DIR, "dados", "raw", "dados.csv")

def carregar_dados_brutos():
    df = pd.read_csv(PATH_RAW, encoding='utf-8-sig')
    
    # CORREÇÃO 2: Limpar nomes das colunas
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
    # Nomes exatos das colunas
    col_nec1 = "Já senti necessidade de apoio emocional durante a graduação."
    col_nec2 = "Eu me sentiria confortável em procurar ajuda dentro da instituição."
    col_nec3 = "Acredito que serviços de apoio podem melhorar a experiência acadêmica dos alunos."
    col_sup = "Eu sinto que há suporte suficiente para dificuldades emocionais na faculdade."
    col_int1 = "Eu já pensei em utilizar o NAP (Núcleo de Apoio Psicopedagógico) em algum momento."
    col_int2 = "Tenho confiança na confidencialidade do atendimento oferecido pelo NAP (Núcleo de Apoio Psicopedagógico)."
    col_int3 = "Eu sei como acessar os serviços oferecidos pelo NAP  (Núcleo de Apoio Psicopedagógico)."
    
    # Converte para numérico
    for col in [col_nec1, col_nec2, col_nec3, col_sup, col_int1, col_int2, col_int3]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            print(f"✅ {col[:40]}... convertida")
        else:
            print(f"❌ Coluna não encontrada: {col[:40]}...")
    
    # CORREÇÃO 3: Cálculo com NaN seguro
    df['score_necessidade'] = df[[col_nec1, col_nec2, col_nec3]].mean(axis=1)
    df['score_suporte'] = df[col_sup]
    df['score_intencao'] = df[[col_int1, col_int2, col_int3]].mean(axis=1)
    
    # CORREÇÃO 4: Gap seguro contra NaN
    df['score_gap'] = df['score_necessidade'].fillna(0) - df['score_suporte'].fillna(0)
    
    print(f"✅ Necessidade média: {df['score_necessidade'].mean():.1f}")
    print(f"✅ Suporte média: {df['score_suporte'].mean():.1f}")
    print(f"✅ Gap média: {df['score_gap'].mean():.1f}")
    
    return df

def calcular_priorizacao(df):
    problemas = []
    col_info = "Eu sei a quem recorrer dentro da faculdade quando tenho dificuldades emocionais."
    if col_info in df.columns:
        df[col_info] = pd.to_numeric(df[col_info], errors='coerce')
        impacto_info = 10 - df[col_info].mean()
        problemas.append({"Problema": "Falta de informação", "Impacto": impacto_info, "Esforço": 2})
    
    col_prec = "Sinto que existe um preconceito em procurar apoio psicológico ou pedagógico na instituição."
    if col_prec in df.columns:
        df[col_prec] = pd.to_numeric(df[col_prec], errors='coerce')
        impacto_prec = df[col_prec].mean()
        problemas.append({"Problema": "Preconceito", "Impacto": impacto_prec, "Esforço": 6})
    
    if problemas:
        df_problemas = pd.DataFrame(problemas)
        df_problemas['Prioridade'] = df_problemas['Impacto'] / df_problemas['Esforço']
        return df_problemas.sort_values('Prioridade', ascending=False)
    return pd.DataFrame()

def limpar_colunas(df):
    # CORREÇÃO EXTRA: Não remover colunas de score
    colunas_remover = [col for col in df.columns if 'Carimbo' in col or 'Declaro' in col or 'E-MAIL' in col or 'convidado' in col]
    return df.drop(columns=colunas_remover, errors='ignore')
