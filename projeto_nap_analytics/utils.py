# utils.py
import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PATH_RAW = os.path.join(BASE_DIR, "dados", "raw", "dados.csv")

def carregar_dados_brutos():
    df = pd.read_csv(PATH_RAW, encoding='utf-8-sig')
    # Limpa nomes das colunas (remove quebras de linha e espaços extras)
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
    # USANDO ÍNDICES DAS COLUNAS (POSIÇÕES FIXAS)
    # Baseado no seu diagnóstico:
    # Índice 0-9: dados demográficos
    # Índice 10: "Considero importante..." (pular)
    # Índice 11: "Eu sinto que há suporte suficiente..." ← SUPORTE
    # Índice 14: "Acredito que serviços..." ← NECESSIDADE 3
    # Índice 17: "Eu me sentiria confortável..." ← NECESSIDADE 2
    # A coluna de NECESSIDADE 1 está fora do range 10-19? Ela está no índice original 10? Vamos usar força bruta
    
    # Vamos localizar as colunas pelo nome, mas com fallback para índices
    col_nec1 = "Já senti necessidade de apoio emocional durante a graduação."
    col_nec2 = "Eu me sentiria confortável em procurar ajuda dentro da instituição."
    col_nec3 = "Acredito que serviços de apoio podem melhorar a experiência acadêmica dos alunos."
    col_sup = "Eu sinto que há suporte suficiente para dificuldades emocionais na faculdade."
    
    # GARANTIR que as colunas existem (pelo diagnóstico, todas existem)
    for col in [col_nec1, col_nec2, col_nec3, col_sup]:
        if col not in df.columns:
            st.error(f"❌ Coluna não encontrada: {col}")
            return df
    
    # FORÇAR a leitura dos valores para cada linha, ignorando NaN
    # Vamos preencher os NaN com a média da coluna para não perder dados
    for col in [col_nec1, col_nec2, col_nec3, col_sup]:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        # Preenche NaN com a média da coluna
        df[col] = df[col].fillna(df[col].mean())
    
    # CRIA OS SCORES
    df['score_necessidade'] = (df[col_nec1] + df[col_nec2] + df[col_nec3]) / 3
    df['score_suporte'] = df[col_sup]
    df['score_gap'] = df['score_necessidade'] - df['score_suporte']
    
    # Intenção (já funcionava)
    col_int1 = "Eu já pensei em utilizar o NAP (Núcleo de Apoio Psicopedagógico) em algum momento."
    col_int2 = "Tenho confiança na confidencialidade do atendimento oferecido pelo NAP (Núcleo de Apoio Psicopedagógico)."
    col_int3 = "Eu sei como acessar os serviços oferecidos pelo NAP  (Núcleo de Apoio Psicopedagógico)."
    
    for col in [col_int1, col_int2, col_int3]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df['score_intencao'] = (df[col_int1] + df[col_int2] + df[col_int3]) / 3
    
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
    colunas_remover = [col for col in df.columns if 'Carimbo' in col or 'Declaro' in col or 'E-MAIL' in col or 'convidado' in col]
    return df.drop(columns=colunas_remover, errors='ignore')
