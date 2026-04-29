# scripts/01_etl.py
import pandas as pd
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import PATH_RAW, PATH_PROCESSED, JORNADA_COL

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

def run_etl():
    print("📥 Carregando dados brutos...")
    df = pd.read_csv(PATH_RAW, encoding='utf-8')
    
    print("🧹 Limpando dados...")
    df = df.replace(r'^\s*$', np.nan, regex=True)
    
    print("🏷️ Criando coluna Jornada...")
    df['Jornada'] = df[JORNADA_COL].apply(classificar_jornada)
    
    colunas_uteis = [col for col in df.columns if 'Carimbo' not in col 
                     and 'Declaro' not in col 
                     and 'INFORME SEU E-MAIL' not in col
                     and 'Você gostaria de ser convidado' not in col]
    df = df[colunas_uteis]
    
    os.makedirs(os.path.dirname(PATH_PROCESSED), exist_ok=True)
    
    print(f"💾 Salvando dados modelados em {PATH_PROCESSED}")
    df.to_csv(PATH_PROCESSED, index=False)
    print(f"✅ ETL concluído. {len(df)} registros processados.")

if __name__ == "__main__":
    run_etl()