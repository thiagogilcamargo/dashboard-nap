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
    # Pega as colunas pelo nome EXATO (copia do seu CSV)
    col_nec = "Já senti necessidade de apoio emocional durante a graduação."
    col_conf = "Eu me sentiria confortável em procurar ajuda dentro da instituição."
    col_acred = "Acredito que serviços de apoio podem melhorar a experiência acadêmica dos alunos."
    col_sup = "Eu sinto que há suporte suficiente para dificuldades emocionais na faculdade."
    
    # Converte para número
    df[col_nec] = pd.to_numeric(df[col_nec], errors='coerce')
    df[col_conf] = pd.to_numeric(df[col_conf], errors='coerce')
    df[col_acred] = pd.to_numeric(df[col_acred], errors='coerce')
    df[col_sup] = pd.to_numeric(df[col_sup], errors='coerce')
    
    # Calcula
    df['score_necessidade'] = (df[col_nec] + df[col_conf] + df[col_acred]) / 3
    df['score_suporte'] = df[col_sup]
    df['score_gap'] = df['score_necessidade'] - df['score_suporte']
    
    # Intenção
    col_int1 = "Eu já pensei em utilizar o NAP (Núcleo de Apoio Psicopedagógico) em algum momento."
    col_int2 = "Tenho confiança na confidencialidade do atendimento oferecido pelo NAP (Núcleo de Apoio Psicopedagógico)."
    col_int3 = "Eu sei como acessar os serviços oferecidos pelo NAP  (Núcleo de Apoio Psicopedagógico)."
    df[col_int1] = pd.to_numeric(df[col_int1], errors='coerce')
    df[col_int2] = pd.to_numeric(df[col_int2], errors='coerce')
    df[col_int3] = pd.to_numeric(df[col_int3], errors='coerce')
    df['score_intencao'] = (df[col_int1] + df[col_int2] + df[col_int3]) / 3
    
    return df

def calcular_priorizacao(df):
    # Versão simplificada
    problemas = []
    try:
        col_info = "Eu sei a quem recorrer dentro da faculdade quando tenho dificuldades emocionais."
        df[col_info] = pd.to_numeric(df[col_info], errors='coerce')
        impacto_info = 10 - df[col_info].mean()
        problemas.append({"Problema": "Falta de informação", "Impacto": impacto_info, "Esforço": 2})
    except:
        pass
    df_problemas = pd.DataFrame(problemas)
    if not df_problemas.empty:
        df_problemas['Prioridade'] = df_problemas['Impacto'] / df_problemas['Esforço']
        return df_problemas.sort_values('Prioridade', ascending=False)
    return pd.DataFrame()

def limpar_colunas(df):
    # NÃO REMOVE NADA IMPORTANTE
    return df
