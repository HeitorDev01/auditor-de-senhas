"""Gera um banco de senhas de exemplo, para o auditor ter o qye analisar"""

import hashlib

def gerar_hash (senha):
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()

contas = [
    ("joao.silva", "123456"),                       # senha vazada
    ("maria.souza", "maria.souza"),                 # senha = nome de usuario
    ("pedro.lima", "sol42"),                        # curta demais
    ("ana.costa", "zxq9k"),                         # curta, mas fora de listas
    ("bruno.dev", "girafa-nuvem-relogio-tijolo"),   # longa e imprevisivel
]