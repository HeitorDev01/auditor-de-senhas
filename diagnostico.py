import os

import pymysql
from dotenv import load_dotenv

# Carrega as variaveis do arquivo .env (se existir).
load_dotenv()


def exigir_env(nome):
    """Le uma variavel de ambiente obrigatoria, com erro claro se faltar."""
    valor = os.environ.get(nome)
    if not valor:
        raise SystemExit(
            "Variavel '{}' nao definida. Crie um arquivo .env "
            "ou defina no terminal antes de rodar.".format(nome)
        )
    return valor


con = pymysql.connect(
    host=os.environ.get("DB_HOST", "localhost"),
    port=int(os.environ.get("DB_PORT", "3306")),
    user=exigir_env("DB_USER"),
    password=exigir_env("DB_PASSWORD"),
    database=os.environ.get("DB_NAME", "auditoria"),
)
with con.cursor() as cursor:
    cursor.execute("SELECT @@port, @@version, @@datadir;")
    print("Python conectou em:", cursor.fetchone())
    cursor.execute("SELECT COUNT(*) FROM usuarios;")
    print("Contas que o Python ve:", cursor.fetchone()[0])
    cursor.execute("SELECT usuario FROM usuarios;")
    print("Usuarios:", [linha[0] for linha in cursor.fetchall()])
con.close()