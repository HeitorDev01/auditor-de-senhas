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
import os

import pymysql
from dotenv import load_dotenv

# Carrega as variaveis do arquivo .env (se existir), para nao precisar
# definir DB_USER/DB_PASSWORD na mao a cada sessao do terminal.
load_dotenv()


def exigir_env(nome):
    """Le uma variavel de ambiente obrigatoria, com erro claro se faltar."""
    valor = os.environ.get(nome)
    if not valor:
        raise SystemExit(
            "Variavel '{}' nao definida. Crie um arquivo .env "
            "(veja .env.example) ou defina no terminal antes de rodar.".format(nome)
        )
    return valor


def gerar_hash (senha):
    """Devole o hash SHA-256 da senha, em texto hexadecimal"""
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()

def carregar_wordlist(caminho):
    """Le um arquivo de senhas, uma por linha, sem quebras"""
    palavras = []

    with open(caminho, "r", encoding="utf-8", errors="ignore") as arquivo:
        for linha in arquivo:
            palavra = linha.strip()
            if palavra:
                palavras.append(palavra)

    return palavras

def carregar_banco_do_mysql():
    conexao = pymysql.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", "3306")),
        user=exigir_env("DB_USER"),
        password=exigir_env("DB_PASSWORD"),
        database=os.environ.get("DB_NAME", "auditoria"),
        charset="utf8mb4",
    )
    try:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT usuario, hash_senha FROM usuarios;")
            linhas = cursor.fetchall()
    finally:
        conexao.close()

    contas = []
    for usuario, hash_da_senha in linhas:
        contas.append({"usuario": usuario, "hash": hash_da_senha})

    return contas

def quebrar_com_wordlist(hash_alvo, palavras):
    """Testa a wordlist contra o hash. Devolve a senha ou None."""
    for palavra in palavras:
        if gerar_hash(palavra) == hash_alvo:
            return palavra

    return None

if __name__ == "__main__":
    contas = carregar_banco_do_mysql()
    vazadas = carregar_wordlist("vazadas.txt")

    print("Banco (MySQL): {} contas".format(len(contas)))
    print("Lista de senhas vazadas: {} encontradas.".format(len(vazadas)))
    print("")

    for conta in contas:
        senha = quebrar_com_wordlist(conta["hash"], vazadas)
        if senha is not None:
            print("{:<14} senha na lista de vazadas: '{}'".format(
                conta["usuario"], senha))
        else:
            print("{:<14} resistiu ao dicionario".format(conta["usuario"]))