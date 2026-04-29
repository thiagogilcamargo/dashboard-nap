# config/config.py
# =====================================
# CONFIGURACOES DO PROJETO NAP
# =====================================
import os

# =====================================
# CAMINHOS (funciona local e na nuvem)
# =====================================
# Detecta onde o script está rodando
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Caminhos absolutos (funcionam em qualquer lugar)
PATH_RAW = os.path.join(BASE_DIR, "dados", "raw", "dados.csv")
PATH_PROCESSED = os.path.join(BASE_DIR, "dados", "processed", "dados_modelados.csv")
PATH_PROBLEMAS = os.path.join(BASE_DIR, "dados", "processed", "problemas_priorizados.csv")
PATH_PDF = os.path.join(BASE_DIR, "outputs", "relatorio_nap.pdf")

# =====================================
# SUAS CONFIGURAÇÕES (INALTERADAS)
# =====================================
PERCEPCAO_COLS = [
    "Já senti necessidade de apoio emocional durante a graduação.",
    "Eu me sentiria confortável em procurar ajuda dentro da instituição.",
    "Eu sinto que há suporte suficiente para dificuldades emocionais na faculdade.",
    "Acredito que serviços de apoio podem melhorar a experiência acadêmica dos alunos."
]

INTENCAO_COLS = [
    "Eu já pensei em utilizar o NAP (Núcleo de Apoio Psicopedagógico) em algum momento.",
    "Tenho confiança na confidencialidade do atendimento oferecido pelo NAP (Núcleo de Apoio Psicopedagógico).",
    "Eu sei como acessar os serviços oferecidos pelo NAP  (Núcleo de Apoio Psicopedagógico)."
]

EXPERIENCIA_COLS = [
    "O atendimento do NAP (Núcleo de Apoio Psicopedagógico) atendeu às minhas expectativas.",
    "Senti que fui ouvido(a) e compreendido(a) no atendimento.",
    "Confio no profissionalismo do atendimento oferecido pelo NAP (Núcleo de Apoio Psicopedagógico).",
    "O atendimento do NAP (Núcleo de Apoio Psicopedagógico) contribuiu para o meu bem-estar emocional.",
    "Eu recomendaria o NAP (Núcleo de Apoio Psicopedagógico) para outros estudantes."
]

ACESSO_COLS = [
    "Eu consegui acessar o NAP (Núcleo de Apoio Psicopedagógico)  com facilidade.",
    "Foi fácil acessar o NAP (Núcleo de Apoio Psicopedagógico) para agendar e verificar horários.",
    "O tempo de espera para atendimento foi adequado."
]

JORNADA_COL = "Quais da opções abaixo melhor representa você em relação ao NAP (Núcleo de Apoio Psicopedagógico)?"

ESFORCO_PROBLEMAS = {
    "Falta de informação": 2,
    "Preconceito": 6,
    "Acesso (horários/local)": 7,
    "Tempo de espera": 8
}
