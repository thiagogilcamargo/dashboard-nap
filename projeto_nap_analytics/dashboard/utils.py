import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH_RAW = os.path.join(BASE_DIR, "dados", "raw", "dados.csv")

JORNADA_COL = "Quais da opções abaixo melhor representa você em relação ao NAP (Núcleo de Apoio Psicopedagógico)?"

# ============================================================
# LOAD
# ============================================================
def carregar_dados_brutos():
    df = pd.read_csv(PATH_RAW, encoding="utf-8-sig")
    df.columns = df.columns.str.replace("\n", " ").str.strip()
    df = df.replace(r"^\s*$", np.nan, regex=True)
    return df

# ============================================================
# JORNADA
# ============================================================
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
    if JORNADA_COL in df.columns:
        df["Jornada"] = df[JORNADA_COL].apply(classificar_jornada)
    else:
        df["Jornada"] = "Indefinido"
    return df

# ============================================================
# SCORES
# ============================================================
def calcular_scores(df):

    cols_necessidade = [
        "Já senti necessidade de apoio emocional durante a graduação.",
        "Eu me sentiria confortável em procurar ajuda dentro da instituição.",
        "Eu sinto que há suporte suficiente para dificuldades emocionais na faculdade."
    ]

    cols_intencao = [
        "Eu já pensei em utilizar o NAP (Núcleo de Apoio Psicopedagógico) em algum momento.",
        "Tenho confiança na confidencialidade do atendimento oferecido pelo NAP (Núcleo de Apoio Psicopedagógico).",
        "Eu sei como acessar os serviços oferecidos pelo NAP  (Núcleo de Apoio Psicopedagógico)."
    ]

    for col in cols_necessidade + cols_intencao:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["score_necessidade"] = df[cols_necessidade].mean(axis=1)
    df["score_intencao"] = df[cols_intencao].mean(axis=1)

    return df

# ============================================================
# LIMPEZA
# ============================================================
def limpar_colunas(df):
    remover = [c for c in df.columns if "Carimbo" in c or "E-MAIL" in c or "Declaro" in c]
    return df.drop(columns=remover, errors="ignore")
