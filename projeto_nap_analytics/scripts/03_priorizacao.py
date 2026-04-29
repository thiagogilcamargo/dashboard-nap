# scripts/03_priorizacao.py
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import PATH_PROCESSED, PATH_PROBLEMAS, ESFORCO_PROBLEMAS

def normalize(series):
    if series.max() == series.min():
        return series * 0
    return (series - series.min()) / (series.max() - series.min())

def run_priorizacao():
    print("🎯 Carregando dados para priorização...")
    df = pd.read_csv(PATH_PROCESSED)
    
    problemas = []
    
    col_info = "Eu sei a quem recorrer dentro da faculdade quando tenho dificuldades emocionais."
    if col_info in df.columns:
        impacto_info = 10 - df[col_info].mean()
        problemas.append({"Problema": "Falta de informação", "Impacto_raw": impacto_info})
    
    col_prec = "Sinto que existe um preconceito em procurar apoio psicológico ou pedagógico na instituição."
    if col_prec in df.columns:
        impacto_prec = df[col_prec].mean()
        problemas.append({"Problema": "Preconceito", "Impacto_raw": impacto_prec})
    
    col_acesso = "Considero o NAP (Núcleo de Apoio Psicopedagógico) acessível em termos de horário e localização."
    if col_acesso in df.columns:
        impacto_acesso = 10 - df[col_acesso].dropna().mean()
        problemas.append({"Problema": "Acesso (horários/local)", "Impacto_raw": impacto_acesso})
    
    col_espera = "O tempo de espera para atendimento foi adequado."
    if col_espera in df.columns:
        impacto_espera = 10 - df[col_espera].dropna().mean()
        problemas.append({"Problema": "Tempo de espera", "Impacto_raw": impacto_espera})
    
    df_problemas = pd.DataFrame(problemas)
    df_problemas['Esforço'] = df_problemas['Problema'].map(ESFORCO_PROBLEMAS)
    df_problemas['Impacto_norm'] = normalize(df_problemas['Impacto_raw'])
    df_problemas['Esforço_norm'] = normalize(df_problemas['Esforço'])
    df_problemas['Prioridade'] = df_problemas['Impacto_norm'] * (1 - df_problemas['Esforço_norm'])
    df_problemas = df_problemas.sort_values('Prioridade', ascending=False)
    
    print("\n📊 Ranking de priorização:")
    for _, row in df_problemas.iterrows():
        print(f"  • {row['Problema']}: prioridade {row['Prioridade']:.3f}")
    
    os.makedirs(os.path.dirname(PATH_PROBLEMAS), exist_ok=True)
    print(f"\n💾 Salvando em {PATH_PROBLEMAS}")
    df_problemas.to_csv(PATH_PROBLEMAS, index=False)
    print("✅ Priorização concluída.")

if __name__ == "__main__":
    run_priorizacao()
