"""
Demonstrar: por que o hashin correto (salt + bcrypt) derrota o auditor.

1)Salt: a MESMA senha gera hases DIFERENTES -> acaba com rainbow tables.
2)Velocidade: bcrypt e  proposital-mente LENTO -> forca bruta fiac inviavel.
3)Projecao: o ataue de forca bruta que levava segundos em SHA-256
 passa a levar mese/ anos em bcrypt.
 
"""
import hashlib
import time
import bcrypt

def sha256(senha):
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()

print("=" * 60)
print("1) SALT: a mesma senha gera hashes DIFERENTES")
print("=" * 60)
senha = "123456"
hash1 = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt())
hash2 = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt())
print("senha :", senha)
print("hash1 :", hash1.decode())
print("hash2 :", hash2.decode())
print("Sao iguais?", hash1 == hash2)
print("SHA-256 puro daira SEMPRE o mesmo:", sha256(senha))
print("verificar senha certa:", bcrypt.checkpw(b"123456", hash1))
print("verificar senha errada:", bcrypt.checkpw(b"000000", hash1))
print("")

print("=" * 60)
print("2) Velocidade: hashes por segundo")
print("=" * 60)
quantidade = 200000
inicio = time.perf_counter()
for i in range(quantidade):
    sha256(str(i))
sha_por_segundo = quantidade / (time.perf_counter() - inicio)