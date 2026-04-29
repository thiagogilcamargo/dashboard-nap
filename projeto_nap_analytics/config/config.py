import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PATH_RAW = os.path.join(BASE_DIR, "dados", "raw", "dados.csv")

JORNADA_COL = "Quais da opções abaixo melhor representa você em relação ao NAP (Núcleo de Apoio Psicopedagógico)?"

NECESSIDADE_COLS = [
    "Já senti necessidade de apoio emocional durante a graduação.",
    "Eu me sentiria confortável em procurar ajuda dentro da instituição.",
    "Acredito que serviços de apoio podem melhorar a experiência acadêmica dos alunos."
]

SUPORTE_COLS = [
    "Eu sinto que há suporte suficiente para dificuldades emocionais na faculdade."
]

INTENCAO_COLS = [
    "Eu já pensei em utilizar o NAP (Núcleo de Apoio Psicopedagógico) em algum momento.",
    "Tenho confiança na confidencialidade do atendimento oferecido pelo NAP (Núcleo de Apoio Psicopedagógico).",
    "Eu sei como acessar os serviços oferecidos pelo NAP  (Núcleo de Apoio Psicopedagógico)."
]

ESFORCO_PROBLEMAS = {
    "Falta de informação": 2,
    "Preconceito": 6,
    "Acesso (horários/local)": 7,
    "Tempo de espera": 8
}
