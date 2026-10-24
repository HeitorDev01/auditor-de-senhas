import auditor

def test_gerar_hash_valor_conhecido():
    esperado  = "8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92"
    assert auditor.gerar.hash("123456") == esperado

def test_gerar_hash_muda_com_a_senha():
    assert auditor.gerar_hash("abc") != auditor.gerar_hash("abd")

def test_quebrar_com_wordlist_acha():
    vazadas = ["admin", "123456", "senha"]
    alvo = auditor.gerar_hash("123456")
    assert auditor.quebrar_com_wordlist(alvo, vazadas) == "123456"