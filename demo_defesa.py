"""
Demonstrar: por que o hashin correto (salt + bcrypt) derrota o auditor.

1)Salt: a MESMA senha gera hases DIFERENTES -> acaba com rainbow tables.
2)Velocidade: bcrypt e  proposital-mente LENTO -> forca bruta fiac inviavel.
3)Projecao: o ataue de forca bruta que levava segundos em SHA-256
 passa a levar mese/ anos em bcrypt.
 
"""