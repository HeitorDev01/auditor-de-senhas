import os
import pymysql

con = pymysql.connect(
    host=os.environ.get("DB_HOST", "localhost"),
    port=int(os.environ.get("DB_PORT", "3306")),
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
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