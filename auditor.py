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
import itertools
import string
import os
import csv
import json

import pymysql
from dotenv import load_dotenv

TAMANHO_MINIMO_SENHA = 8  # tamanho minimo de senha aceitavel
TAMANHO_MAXIMO_BRUTA = 5  # tamanho maximo de senha a ser testada por forca bruta
ARQUIVO_WORDLIST = "vazadas.txt"  # arquivo de senhas vazadas, uma por linha
ARQUIVO_CSV = "relatorio.csv"  # arquivo de saida em CSV
ARQUIVO_JSON = "relatorio.json"  # arquivo de saida em JSON
ALFABETO_FORCA_BRUTA = string.ascii_lowercase + string.digits  # alfabeto para testes de forca bruta
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

def forca_bruta(hash_alvo, tamanho_maximo):
    for tamanho in range(1, tamanho_maximo + 1):
        for combinacao in itertools.product(ALFABETO_FORCA_BRUTA, repeat=tamanho):
            tentativa = "".join(combinacao)
            if gerar_hash(tentativa) == hash_alvo:
                return tentativa
    return None


def recuperar_senha(usuario, hash_armazenado, vazadas, tamanho_bruta):
    recuperada = quebrar_com_wordlist(hash_armazenado, vazadas)
    if recuperada is not None:
        return recuperada, "vazada"

    if gerar_hash(usuario) == hash_armazenado:
        return usuario, "igual_ao_usuario"

    print("     ... testando forca bruta em '{}' (ate {} caracteres, pode demorar)".format(usuario, tamanho_bruta))
    recuperada = forca_bruta(hash_armazenado, tamanho_bruta)
    if recuperada is not None:
        return recuperada, "forca_bruta"
    return None, None

def classificar_conta(usuario, hash_armazenamento, vazadas, tamanho_bruta):
    senha, origem =  recuperar_senha(usuario, hash_armazenamento, vazadas, tamanho_bruta)

    if senha is None:
        return{
            "usuario": usuario,
            "nivel": "OK",
            "senha": None,
            "motivos":["resistiu a todos os testes (dicionario, usuario e forca bruta)"] ,
        }

    motivos = []
    if origem == "vazada":
        motivos.append("consta em lista de senhas vazadas")
    if origem == "igual_ao_usuario":
        motivos.append("igual ao nome de usuario")
    if origem == "forca_bruta":
        motivos.append("descoberta por forca bruta (ate {} caracteres)".format(tamanho_bruta))
    if len(senha) < TAMANHO_MINIMO_SENHA:
        motivos.append("curta demais ({}caracteres)".format(len(senha)))
    if senha.isdigit():
        motivos.append("composta apenas por numeros")

    nivel = "CRITICA" if origem == "vazada" else "ALTA"

    return {"usuario": usuario, "nivel": nivel, "senha": senha, "motivos": motivos}

def exportar_csv(resultados, caminho):
    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["usuario", "nivel", "senha_recuperada", "motivos"])
        for r in resultados:
            senha = r["senha"] if r["senha"] is not None else ""
            motivos = "; ".join(r["motivos"])
            escritor.writerow([r["usuario"], r["nivel"], senha, motivos])

def exportar_json(resultados, caminho):
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(resultados, arquivo, ensure_ascii=False, indent=2)

def imprimir_relatorio(resultados, contadores,qtd_contas,qtd_vazadas):
    print("=" * 48)
    print("   RELATORIO DE AUDITORIA DE SENHAS")
    print("=" * 48)
    print("Banco (MySQL): {} contas".format(qtd_contas))
    print("Lista de senhas vazadas: {} encontradas.".format(qtd_vazadas))
    print("")

    for resultado in resultados:
        print(" [{:<7}] {}".format(resultado["nivel"], resultado["usuario"]))
        if resultado["senha"] is not None:
            print("      ... senha encontrada: '{}'".format(resultado["senha"]))
        for motivo in resultado["motivos"]:
            print("             - {}".format(motivo))
        print("")

    print("=" * 48)
    print("Resumo: {} criticas, {} altas, {} ok".format(
        contadores["CRITICA"], contadores["ALTA"], contadores["OK"]
    ))

    total_fracas = contadores["CRITICA"] + contadores["ALTA"]
    if total_fracas > 0:
        print("Acao recomendada: forcar troca de senha de {} contas(s).".format(total_fracas))
    else:
        print("Nenhuma senha fraca encontrada nos testes.")


if __name__ == "__main__":
    TAMANHO_MAXIMO_BRUTA = 5
    contas = carregar_banco_do_mysql()
    vazadas = carregar_wordlist(ARQUIVO_WORDLIST)

    print("=" * 48)
    print("   RELATORIO DE AUDITORIA DE SENHAS")
    print("=" * 48)
    print("Banco (MySQL): {} contas".format(len(contas)))
    print("Lista de senhas vazadas: {} encontradas.".format(len(vazadas)))
    print("(forca bruta ligata ate {} caracteres - pode levar ~1 min)".format(TAMANHO_MAXIMO_BRUTA))
    print("")

    resultados = []
    contadores = {"CRITICA": 0, "ALTA": 0, "OK": 0}
    
    for conta in contas:
        resultado = classificar_conta(conta["usuario"], conta["hash"], vazadas, TAMANHO_MAXIMO_BRUTA)
        resultados.append(resultado)
        contadores[resultado["nivel"]] += 1

        print(" [{:<7}] {}".format(resultado["nivel"], resultado["usuario"]))
        if resultado["senha"] is not None:
            print("      ... senha encontrada: '{}'".format(resultado["senha"]))
        for motivo in resultado["motivos"]:
            print("             - {}".format(motivo))
        print("")

    print("=" * 48)
    print("Resumo: {} criticas, {} altas, {} ok".format(
        contadores["CRITICA"], contadores["ALTA"], contadores["OK"]
    ))

    total_fracas = contadores["CRITICA"] + contadores["ALTA"]
    if total_fracas > 0:
        print("Acao recomendada: forcar troca de senha de {} contas(s).".format(total_fracas))
    else:
        print("Nenhuma senha fraca encontrada nos testes.")

    exportar_csv(resultados, "relatorio.csv")
    exportar_json(resultados, "relatorio.json")
    print("")
    print("Relatorios salvos: relatorio.csv e relatorio.json")
