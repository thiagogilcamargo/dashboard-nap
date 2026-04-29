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
    # PERCEPÇÃO (score_percepcao)
    # ============================================================
    col_perc1 = "Já senti necessidade de apoio emocional durante a graduação."
    col_perc2 = "Eu me sentiria confortável em procurar ajuda dentro da instituição."
    col_perc3 = "Eu sinto que há suporte suficiente para dificuldades emocionais na faculdade."
    col_perc4 = "Acredito que serviços de apoio podem melhorar a experiência acadêmica dos alunos."
    
    for col in [col_perc1, col_perc2, col_perc3, col_perc4]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df['score_percepcao'] = df[[col_perc1, col_perc2, col_perc3, col_perc4]].mean(axis=1)
    
    # ============================================================
    # NECESSIDADE (média das perguntas 1, 2 e 4 - sem suporte)
    # ============================================================
    df['score_necessidade'] = df[[col_perc1, col_perc2, col_perc4]].mean(axis=1)
    
    # ============================================================
    # SUPORTE (apenas a pergunta 3)
    # ============================================================
    df['score_suporte'] = df[col_perc3]
    
    # ============================================================
    # GAP
    # ============================================================
    df['score_gap'] = df['score_necessidade'] - df['score_suporte']
    
    # ============================================================
    # INTENÇÃO
    # ============================================================
    col_int1 = "Eu já pensei em utilizar o NAP (Núcleo de Apoio Psicopedagógico) em algum momento."
    col_int2 = "Tenho confiança na confidencialidade do atendimento oferecido pelo NAP (Núcleo de Apoio Psicopedagógico)."
    col_int3 = "Eu sei como acessar os serviços oferecidos pelo NAP  (Núcleo de Apoio Psicopedagógico)."
    
    for col in [col_int1, col_int2, col_int3]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df['score_intencao'] = df[[col_int1, col_int2, col_int3]].mean(axis=1)
    
    # ============================================================
    # EXPERIÊNCIA (apenas para quem usou - mantido para compatibilidade)
    # ============================================================
    col_exp1 = "O atendimento do NAP (Núcleo de Apoio Psicopedagógico) atendeu às minhas expectativas."
    col_exp2 = "Senti que fui ouvido(a) e compreendido(a) no atendimento."
    
    for col in [col_exp1, col_exp2]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df['score_experiencia'] = df[[col_exp1, col_exp2]].mean(axis=1)
    
    # ============================================================
    # ACESSO (apenas para quem usou)
    # ============================================================
    col_acesso1 = "Eu consegui acessar o NAP (Núcleo de Apoio Psicopedagógico)  com facilidade."
    col_acesso2 = "Foi fácil acessar o NAP (Núcleo de Apoio Psicopedagógico) para agendar e verificar horários."
    
    for col in [col_acesso1, col_acesso2]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df['score_acesso'] = df[[col_acesso1, col_acesso2]].mean(axis=1)
    
    # Preencher NaNs com a média da coluna (para não quebrar o dashboard)
    for score in ['score_percepcao', 'score_necessidade', 'score_suporte', 'score_gap', 
                  'score_intencao', 'score_experiencia', 'score_acesso']:
        if score in df.columns:
            media = df[score].mean()
            df[score] = df[score].fillna(media)
    
    # Debug
    print("=" * 50)
    print("📊 SCORES CALCULADOS:")
    print(f"   score_percepcao: {df['score_percepcao'].mean():.1f}")
    print(f"   score_necessidade: {df['score_necessidade'].mean():.1f}")
    print(f"   score_suporte: {df['score_suporte'].mean():.1f}")
    print(f"   score_gap: {df['score_gap'].mean():.1f}")
    print(f"   score_intencao: {df['score_intencao'].mean():.1f}")
    print("=" * 50)
    
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
    
    return pd.DataFrame([{"Problema": "Falta de informação", "Impacto": 7.5, "Esforço": 2, "Prioridade": 3.75}])

def limpar_colunas(df):
    colunas_remover = [col for col in df.columns if 'Carimbo' in col or 'Declaro' in col or 'E-MAIL' in col or 'convidado' in col]
    return df.drop(columns=colunas_remover, errors='ignore')
