# run_pipeline.py
import subprocess
import sys
import os

print("\n" + "=" * 60)
print("🚀 PIPELINE NAP - ANÁLISE COMPLETA")
print("=" * 60)

scripts = [
    ("scripts/01_etl.py", "ETL e modelagem"),
    ("scripts/02_scores.py", "Cálculo de scores"),
    ("scripts/03_priorizacao.py", "Priorização de problemas"),
    ("scripts/04_pdf_relatorio.py", "Geração do PDF executivo")
]

for script, desc in scripts:
    print(f"\n▶️ {desc}...")
    result = subprocess.run([sys.executable, script])
    if result.returncode != 0:
        print(f"❌ Erro em {script}. Pipeline interrompido.")
        sys.exit(1)

print("\n" + "=" * 60)
print("✅ PIPELINE CONCLUÍDO COM SUCESSO!")
print("📄 Relatório PDF: outputs/relatorio_nap.pdf")
print("📊 Dashboard: streamlit run dashboard/app.py")
print("=" * 60 + "\n")