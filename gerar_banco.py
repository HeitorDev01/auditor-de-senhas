"""
Auditor de senhas - Etapa 1: Ler o bando e casar com o cracker.

Roda DENTRO da organizaçao com autorizacao sobre o banco de senhas dela. 
O objetivo é defensivo: descobrir quais senhas sao fracas ANTES
que um atacante descubra, e forçar a troca.

O banco tem uma conta por linha no formato:
usuario:hash

Nenhuma senha em texto - só o hash como um sistema de verdae guarda.
"""

import hashlib

def gerar_hash (senha):
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()

def carregar_wordlist(caminho):
    palavras = []

    with open(caminho, "r", encoding="utf-8", erros="ignore") as arquivo:
        for linha in arquivo:
            palavra = linha.strip()
            if palavra:
                palavras.append(palavras)