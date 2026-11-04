import auditor


def test_gerar_hash_valor_conhecido():
    esperado = "8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92"
    assert auditor.gerar_hash("123456") == esperado


def test_gerar_hash_muda_com_a_senha():
    assert auditor.gerar_hash("abc") != auditor.gerar_hash("abd")


def test_quebrar_com_wordlist_acha():
    vazadas = ["admin", "123456", "senha"]
    alvo = auditor.gerar_hash("123456")
    assert auditor.quebrar_com_wordlist(alvo, vazadas) == "123456"


def test_quebrar_com_wordlist_nao_acha():
    vazadas = ["admin", "123456"]
    alvo = auditor.gerar_hash("naoexiste")
    assert auditor.quebrar_com_wordlist(alvo, vazadas) is None


def test_forca_bruta_acha_curta():
    alvo = auditor.gerar_hash("ab")
    assert auditor.forca_bruta(alvo, 3) == "ab"


def test_forca_bruta_nao_acha_dentro_do_limite():
    alvo = auditor.gerar_hash("abcdef")  # 6 caracteres
    assert auditor.forca_bruta(alvo, 2) is None


def test_recuperar_senha_por_wordlist():
    vazadas = ["123456"]
    alvo = auditor.gerar_hash("123456")
    assert auditor.recuperar_senha("joao", alvo, vazadas, 2) == ("123456", "vazada")


def test_recuperar_senha_igual_ao_usuario():
    alvo = auditor.gerar_hash("maria")
    assert auditor.recuperar_senha("maria", alvo, [], 2) == ("maria", "igual_ao_usuario")


def test_recuperar_senha_por_forca_bruta():
    alvo = auditor.gerar_hash("ab")
    senha, origem = auditor.recuperar_senha("joao", alvo, [], 3)
    assert senha == "ab"
    assert origem == "forca_bruta"


def test_recuperar_senha_resiste():
    alvo = auditor.gerar_hash("senhabemlongaequenaocai")
    assert auditor.recuperar_senha("joao", alvo, [], 2) == (None, None)


def test_classificar_vazada_e_critica():
    vazadas = ["123456"]
    alvo = auditor.gerar_hash("123456")
    r = auditor.classificar_conta("joao", alvo, vazadas, 2)
    assert r["nivel"] == "CRITICA"
    assert "consta em lista de senhas vazadas" in r["motivos"]


def test_classificar_igual_usuario_e_alta():
    alvo = auditor.gerar_hash("maria")
    r = auditor.classificar_conta("maria", alvo, [], 2)
    assert r["nivel"] == "ALTA"
    assert "igual ao nome de usuario" in r["motivos"]


def test_classificar_forca_bruta_e_alta():
    alvo = auditor.gerar_hash("ab")
    r = auditor.classificar_conta("joao", alvo, [], 3)
    assert r["nivel"] == "ALTA"
    assert any("forca bruta" in m for m in r["motivos"])


def test_classificar_resistente_e_ok():
    alvo = auditor.gerar_hash("senhabemlongaequenaocai")
    r = auditor.classificar_conta("joao", alvo, [], 2)
    assert r["nivel"] == "OK"
    assert r["senha"] is None

def test_entropia_vazia_e_zero():
    assert auditor.estimar_entropia("") == 0.0

def test_entropia_cresce_com_o_tamanho():
    assert auditor.estimar_entropia("abcdef") > auditor.estimar_entropia("abc")

def test_entropia_cresce_com_variedade():
    assert auditor.estimar_entropia("aB3$") > auditor.estimar_entropia("abcd")

def test_entropia_valor_conhecido():
    # 4 digitos: alfabeto de 10 -> 4 * log2(10) = 13.29 bits
    assert round(auditor.estimar_entropia("1234"), 2) == 13.29

def test_rotulos_nos_limites():
    assert auditor.rotular_forca(27.9) == "muito fraca"
    assert auditor.rotular_forca(28) == "fraca"