# 🔐 Auditor de Senhas

Uma ferramenta **defensiva** de segurança que descobre quais senhas de uma organização são fracas — **antes** que um atacante descubra.

---

## 📌 Por que esse projeto existe?

Todo sistema guarda as senhas dos usuários em forma de **hash** (um código embaralhado), nunca em texto puro. O problema é que **um hash fraco não protege uma senha fraca**: se alguém usa `123456`, o hash dela é sempre o mesmo e já é conhecido por qualquer atacante.

Na prática, a maioria dos vazamentos de dados acontece porque usuários escolhem senhas óbvias — o nome de usuário, uma sequência de números, ou algo que já apareceu em listas de senhas vazadas na internet.

Este auditor age como um **"atacante do bem"**: ele roda **dentro da organização, com autorização**, pega o banco de senhas e tenta quebrá-lo usando as mesmas técnicas que um invasor usaria. Tudo que ele conseguir quebrar é exatamente o que precisa ser trocado com urgência.

> 🎯 **Objetivo:** encontrar as senhas fracas primeiro e forçar a troca, reduzindo o risco antes que vire um incidente real.

---

## ⚙️ Como funciona?

O programa lê cada conta do banco (`usuario : hash`) e tenta descobrir a senha original por três caminhos, nesta ordem:

| Etapa | O que faz | Exemplo |
|-------|-----------|---------|
| 1️⃣ **Lista de vazadas** | Compara com senhas que já vazaram publicamente (`vazadas.txt`) | `123456`, `password`, `qwerty` |
| 2️⃣ **Igual ao usuário** | Testa se a senha é o próprio nome de usuário | `maria.souza` com senha `maria.souza` |
| 3️⃣ **Força bruta** | Testa todas as combinações curtas (até 5 caracteres) | `sol42`, `zxq9k` |

Se **nenhuma** técnica quebrar a senha, a conta é marcada como **OK** ✅.

Cada conta recebe um nível de risco:

- 🔴 **CRÍTICA** — senha consta em lista de vazamentos (risco imediato)
- 🟠 **ALTA** — senha foi quebrada por ser óbvia, curta ou igual ao usuário
- 🟢 **OK** — resistiu a todos os testes

> 🔒 **Importante:** o programa nunca vê senhas em texto no banco. Ele só trabalha com os hashes, exatamente como um sistema real faz.

---

## 📊 Exemplo de relatório

Ao rodar, o auditor imprime um resumo no terminal e salva dois arquivos: `relatorio.csv` (para abrir no Excel) e `relatorio.json` (para integrar com outros sistemas).

### No terminal

```
================================================
   RELATORIO DE AUDITORIA DE SENHAS
================================================
Banco (MySQL): 5 contas
Lista de senhas vazadas: 15 encontradas.

 [CRITICA] joao.silva
      ... senha encontrada: '123456'
             - consta em lista de senhas vazadas
             - composta apenas por numeros

 [ALTA   ] maria.souza
      ... senha encontrada: 'maria.souza'
             - igual ao nome de usuario

 [OK     ] bruno.dev
             - resistiu a todos os testes

================================================
Resumo: 1 criticas, 3 altas, 1 ok
Acao recomendada: forcar troca de senha de 4 conta(s).
```

### Arquivo `relatorio.csv`

| usuario | nivel | senha_recuperada | motivos |
|---------|-------|------------------|---------|
| joao.silva | CRITICA | 123456 | consta em lista de senhas vazadas; composta apenas por numeros |
| maria.souza | ALTA | maria.souza | igual ao nome de usuario |
| pedro.lima | ALTA | sol42 | descoberta por forca bruta (ate 5 caracteres) |
| bruno.dev | OK | | resistiu a todos os testes |

### Arquivo `relatorio.json`

```json
[
  {
    "usuario": "joao.silva",
    "nivel": "CRITICA",
    "senha": "123456",
    "motivos": [
      "consta em lista de senhas vazadas",
      "composta apenas por numeros"
    ]
  },
  {
    "usuario": "bruno.dev",
    "nivel": "OK",
    "senha": null,
    "motivos": [
      "resistiu a todos os testes (dicionario, usuario e forca bruta)"
    ]
  }
]
```

> ⚠️ Os relatórios reais contêm senhas em texto e **não devem ser versionados no Git** — por isso ficam no `.gitignore`. Os exemplos acima são apenas ilustrativos.

---

## 🚀 Como usar

### 1. Pré-requisitos

- Python 3.8 ou superior
- Um banco MySQL com uma tabela `usuarios` contendo as colunas `usuario` e `hash_senha`

### 2. Instalação

```bash
# Crie e ative um ambiente virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

# Instale as dependências
pip install -r requirements.txt
```

### 3. Configuração

Copie o arquivo de exemplo e preencha com os dados do seu banco:

```bash
copy .env.example .env        # Windows
# cp .env.example .env        # Linux/Mac
```

Edite o `.env`:

```ini
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=3306
DB_NAME=auditoria
```

> 🔑 O arquivo `.env` guarda a senha do banco e **nunca** vai para o Git.

### 4. Testando a conexão (opcional)

Antes de rodar a auditoria completa, confirme que o Python enxerga o banco:

```bash
python diagnostico.py
```

### 5. Rodando a auditoria

```bash
python auditor.py
```

Ao final, confira o resumo no terminal e os arquivos `relatorio.csv` e `relatorio.json`.

---

## 📁 Estrutura do projeto

```
auditor/
├── auditor.py          # Programa principal: lê o banco e audita as senhas
├── diagnostico.py      # Testa a conexão com o MySQL
├── vazadas.txt         # Lista de senhas vazadas (dicionário de ataque)
├── requirements.txt    # Dependências do projeto
├── .env.example        # Modelo de configuração
├── .env                # Configuração real (ignorado pelo Git)
├── relatorio.csv       # Relatório gerado (ignorado pelo Git)
└── relatorio.json      # Relatório gerado (ignorado pelo Git)
```

---

## 🛡️ Como se defender: por que bcrypt vence SHA-256

Encontrar as senhas fracas é metade do trabalho. A outra metade é **guardar as senhas de forma que a força bruta deixe de valer a pena**. É aí que o algoritmo de hash faz diferença.

### 1. Salt: cada hash é único

Um bom algoritmo de senha adiciona um **salt** — um valor aleatório — a cada senha antes de gerar o hash. Isso torna **rainbow tables inúteis**: o atacante não consegue pré-calcular uma tabela de "hash → senha", porque cada hash do mundo é único. No SHA-256 puro, `123456` sempre vira o mesmo hash — por isso ele é vulnerável.

### 2. Lentidão proposital: força bruta deixa de ser viável

bcrypt é **deliberadamente lento**. Medição em uma máquina comum:

| Algoritmo | Hashes por segundo |
|-----------|--------------------|
| SHA-256   | ~1.040.000         |
| bcrypt    | ~4                 |

bcrypt é cerca de **295.000× mais lento** — e isso é uma vantagem de segurança. Projetando no ataque de força bruta deste projeto:

| Força bruta           | SHA-256 (rápido) | bcrypt (correto) |
|-----------------------|------------------|------------------|
| Senha de 5 caracteres | ~58 segundos     | **~198 dias**    |
| Senha de 6 caracteres | ~35 minutos      | **~20 anos**     |

### Conclusão

A senha **fraca continua fraca** — `123456` cai num ataque de dicionário com ou sem bcrypt, porque é previsível. O que o bcrypt protege é contra **força bruta** de senhas imprevisíveis. A defesa real combina as duas coisas:

- **Hashing lento e salgado** (bcrypt ou argon2), nunca SHA-256/MD5 puros.
- **Senhas longas e imprevisíveis**, que explodem o espaço de busca.

---

## ⚖️ Uso responsável

Esta ferramenta foi feita para uso **defensivo e autorizado**. Rode-a apenas em bancos de senhas da sua própria organização, com permissão explícita. Usar técnicas de quebra de senha contra sistemas de terceiros sem autorização é ilegal.
