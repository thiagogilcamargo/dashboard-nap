# utils.py
import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_RAW = os.path.join(BASE_DIR, "dados", "raw", "dados.csv")

def carregar_dados_brutos():
    # Usando encoding correto
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
    # DEBUG: Mostrar colunas encontradas (vai aparecer nos logs do Streamlit)
    print("=== COLUNAS ENCONTRADAS PARA SCORES ===")
    for col in df.columns:
        if 'necessidade' in col.lower() or 'suporte' in col.lower() or 'confortável' in col.lower() or 'acredito' in col.lower():
            print(f"  - {col}")
    
    # Necessidade (média de 3 perguntas)
    col_nec1 = "Já senti necessidade de apoio emocional durante a graduação."
    col_nec2 = "Eu me sentiria confortável em procurar ajuda dentro da instituição."
    col_nec3 = "Acredito que serviços de apoio podem melhorar a experiência acadêmica dos alunos."
    
    # Suporte (1 pergunta)
    col_sup = "Eu sinto que há suporte suficiente para dificuldades emocionais na faculdade."
    
    # Intenção (3 perguntas)
    col_int1 = "Eu já pensei em utilizar o NAP (Núcleo de Apoio Psicopedagógico) em algum momento."
    col_int2 = "Tenho confiança na confidencialidade do atendimento oferecido pelo NAP (Núcleo de Apoio Psicopedagógico)."
    col_int3 = "Eu sei como acessar os serviços oferecidos pelo NAP  (Núcleo de Apoio Psicopedagógico)."
    
    # Converter para numérico
    for col in [col_nec1, col_nec2, col_nec3, col_sup, col_int1, col_int2, col_int3]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            print(f"✅ Coluna encontrada: {col[:50]}...")
        else:
            print(f"❌ Coluna NÃO encontrada: {col[:50]}...")
    
    # Calcular Necessidade
    if col_nec1 in df.columns and col_nec2 in df.columns and col_nec3 in df.columns:
        df['score_necessidade'] = df[[col_nec1, col_nec2, col_nec3]].mean(axis=1)
        print(f"✅ Necessidade calculada: média {df['score_necessidade'].mean():.1f}")
    else:
        print("❌ Colunas de necessidade não encontradas")
    
    # Calcular Suporte
    if col_sup in df.columns:
        df['score_suporte'] = df[col_sup]
        print(f"✅ Suporte calculado: média {df['score_suporte'].mean():.1f}")
    else:
        print("❌ Coluna de suporte não encontrada")
    
    # Calcular Gap
    if 'score_necessidade' in df.columns and 'score_suporte' in df.columns:
        df['score_gap'] = df['score_necessidade'] - df['score_suporte']
        print(f"✅ Gap calculado: média {df['score_gap'].mean():.1f}")
    
    # Calcular Intenção
    if col_int1 in df.columns and col_int2 in df.columns and col_int3 in df.columns:
        df['score_intencao'] = df[[col_int1, col_int2, col_int3]].mean(axis=1)
        print(f"✅ Intenção calculada: média {df['score_intencao'].mean():.1f}")
    
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
        if df_problemas['Impacto'].max() != df_problemas['Impacto'].min():
            df_problemas['Impacto_norm'] = (df_problemas['Impacto'] - df_problemas['Impacto'].min()) / (df_problemas['Impacto'].max() - df_problemas['Impacto'].min())
        else:
            df_problemas['Impacto_norm'] = 0
        df_problemas['Esforço_norm'] = (df_problemas['Esforço'] - df_problemas['Esforço'].min()) / (df_problemas['Esforço'].max() - df_problemas['Esforço'].min())
        df_problemas['Prioridade'] = df_problemas['Impacto_norm'] * (1 - df_problemas['Esforço_norm'])
        return df_problemas.sort_values('Prioridade', ascending=False)
    
    return pd.DataFrame()

def limpar_colunas(df):
    colunas_remover = [col for col in df.columns if 'Carimbo' in col or 'Declaro' in col or 'E-MAIL' in col or 'convidado' in col]
    return df.drop(columns=colunas_remover, errors='ignore')
