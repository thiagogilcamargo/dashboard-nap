# scripts/04_pdf_relatorio.py
from fpdf import FPDF
import pandas as pd
import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import PATH_PROCESSED, PATH_PROBLEMAS, PATH_PDF

class PDFRelatorio(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(33, 37, 41)
        self.cell(0, 10, 'NAP - Diagnóstico Executivo', 0, 1, 'C')
        self.set_font('Helvetica', 'I', 9)
        self.set_text_color(108, 117, 125)
        self.cell(0, 6, 'Núcleo de Apoio Psicopedagógico', 0, 1, 'C')
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(108, 117, 125)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

def gerar_pdf():
    df = pd.read_csv(PATH_PROCESSED)
    problemas = pd.read_csv(PATH_PROBLEMAS)

    pdf = PDFRelatorio()
    pdf.add_page()
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(33, 37, 41)

    pdf.cell(0, 8, f"Data da análise: {datetime.now().strftime('%d/%m/%Y')}", 0, 1)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 12, f"Total de respondentes: {len(df)}", 0, 1)

    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_fill_color(238, 242, 247)
    pdf.cell(0, 10, "Funil de Jornada", 0, 1, fill=True)
    pdf.set_font('Helvetica', '', 10)
    for grupo, count in df['Jornada'].value_counts().items():
        pct = count / len(df) * 100
        pdf.cell(0, 8, f"• {grupo}: {count} ({pct:.1f}%)", 0, 1)

    pdf.ln(4)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_fill_color(238, 242, 247)
    pdf.cell(0, 10, "Scores por Dimensão (0-10)", 0, 1, fill=True)
    pdf.set_font('Helvetica', '', 10)
    for dim in ['score_percepcao', 'score_intencao', 'score_experiencia', 'score_acesso']:
        if dim in df.columns:
            media = df[dim].dropna().mean()
            nome = dim.replace('score_', '').capitalize()
            pdf.cell(0, 8, f"• {nome}: {media:.1f}", 0, 1)

    pdf.ln(4)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_fill_color(238, 242, 247)
    pdf.cell(0, 10, "Recomendação Estratégica", 0, 1, fill=True)
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(33, 37, 41)
    if len(problemas) > 0:
        pdf.multi_cell(0, 8, problemas.iloc[0]['Problema'] + " — Este é o problema com maior prioridade. Recomenda-se ação imediata.")

    os.makedirs(os.path.dirname(PATH_PDF), exist_ok=True)
    pdf.output(PATH_PDF)
    print(f"✅ PDF gerado: {PATH_PDF}")

if __name__ == "__main__":
    gerar_pdf()