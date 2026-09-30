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
    """Devole o hash SHA-256 da senha, em texto hexadecimal"""
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()

def carregar_wordlist(caminho):
    """Le um arquivo de senhas, uma por linha, sem quebras"""
    palavras = []

    with open(caminho, "r", encoding="utf-8", erros="ignore") as arquivo:
        for linha in arquivo:
            palavra = linha.strip()
            if palavra:
                palavras.append(palavras)
    return palavras

def carregar_banco(caminho):
    """le o banco 'usuario:hash' e devolve uma lista de contas."""
    contas = []

    with open(caminho, "r", encoding="utf-8", errors="ignore") as arquivo:
        for numero, linha in enumerate(arquivo, start=1):
            linha = linha.strip()
            if not linha:
                continue

            if ":" not in linha:
                print("    [aviso] linha {} sem ':' - ignorada".format(numero))
                continue

            usuario, hash_da_senha = linha.split(":", 1)
            contas.append({
                "usuario": usuario,
                "hash": hash_da_senha,
            })

    return contas

def quebrar_com_wordlist(hash_alvo, palavras):
    """Testa a wordlist contra o hash. Devolve a senha ou None."""
    for palavra in palavras:
        if gerar_hash(palavra) == hash_alvo:
            return palavra

    return None

if __name__ == "__main__":
    contas = carregar_banco("banco_de_senhas.txt")
    vazadas = carregar_wordlist("vazadas.txt")

    print("Banco: {} contas".format(len(contas)))
    print("Lista de senhas vazadas: {} encontradas.".format(len(vazadas)))
    print("")

    for conta in contas:
        senha = quebrar_com_wordlist(conta[hash], vazadas)
        if senha is not None:
            print("{:<14} senha na lista de vazadas: '{}'".format(
                conta["usuario"],senha))
        else:
            print("     {:<14} resistiu ao dicionario".format(conta["usuario"]))