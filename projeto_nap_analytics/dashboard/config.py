# dashboard/config.py
import os

# ============================================================
# CAMINHOS DOS ARQUIVOS
# ============================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH_RAW = os.path.join(BASE_DIR, "dados", "raw", "dados.csv")

# ============================================================
# COLUNA DA JORNADA
# ============================================================
JORNADA_COL = "Quais da opções abaixo melhor representa você em relação ao NAP (Núcleo de Apoio Psicopedagógico)?"

# ============================================================
# PERGUNTAS DO QUESTIONÁRIO
# ============================================================

# Necessidade (percepção de falta de apoio)
NECESSIDADE_COLS = [
    "Já senti necessidade de apoio emocional durante a graduação.",
    "Eu me sentiria confortável em procurar ajuda dentro da instituição.",
    "Acredito que serviços de apoio podem melhorar a experiência acadêmica dos alunos."
]

# Suporte (percepção de que a faculdade oferece ajuda)
SUPORTE_COLS = [
    "Eu sinto que há suporte suficiente para dificuldades emocionais na faculdade."
]

# Intenção (disposição a usar o NAP)
INTENCAO_COLS = [
    "Eu já pensei em utilizar o NAP (Núcleo de Apoio Psicopedagógico) em algum momento.",
    "Tenho confiança na confidencialidade do atendimento oferecido pelo NAP (Núcleo de Apoio Psicopedagógico).",
    "Eu sei como acessar os serviços oferecidos pelo NAP (Núcleo de Apoio Psicopedagógico)."
]

# ============================================================
# PERGUNTAS PARA CORRELAÇÃO (todas juntas)
# ============================================================
CORRELACAO_COLS = NECESSIDADE_COLS + SUPORTE_COLS + INTENCAO_COLS

# ============================================================
# NOMES CURTOS PARA EXIBIÇÃO NOS GRÁFICOS
# ============================================================
NOMES_CURTOS = {
    "Já senti necessidade de apoio emocional durante a graduação.": "Necessidade",
    "Eu me sentiria confortável em procurar ajuda dentro da instituição.": "Conforto",
    "Eu sinto que há suporte suficiente para dificuldades emocionais na faculdade.": "Suporte",
    "Acredito que serviços de apoio podem melhorar a experiência acadêmica dos alunos.": "Crença",
    "Eu já pensei em utilizar o NAP (Núcleo de Apoio Psicopedagógico) em algum momento.": "Intenção",
    "Tenho confiança na confidencialidade do atendimento oferecido pelo NAP (Núcleo de Apoio Psicopedagógico).": "Confiança",
    "Eu sei como acessar os serviços oferecidos pelo NAP (Núcleo de Apoio Psicopedagógico).": "Acesso"
}

# ============================================================
# PROBLEMAS E ESFORÇOS (para priorização)
# ============================================================
ESFORCO_PROBLEMAS = {
    "Falta de informação": 2,
    "Preconceito": 6,
    "Acesso (horários/local)": 7,
    "Tempo de espera": 8
}

# ============================================================
# CORES PARA GRÁFICOS
# ============================================================
CORES = {
    "necessidade": "#e74c3c",  # vermelho
    "suporte": "#3498db",      # azul
    "intencao": "#2ecc71",     # verde
    "gap": "#f39c12",          # laranja
    "positivo": "#27ae60",     # verde escuro
    "negativo": "#c0392b",     # vermelho escuro
}

# ============================================================
# LIMIARES PARA ALERTAS
# ============================================================
LIMIARES = {
    "gap_critico": 3.0,           # gap acima disso é crítico
    "pct_alerta": 20,             # percentual que acende alerta
    "pct_critico": 40,            # percentual que acende crítico
}
