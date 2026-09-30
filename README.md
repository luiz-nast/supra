<div align="center">

# ⌨️ supra

**Guarde seus trechos de código e texto. Depois, redigite por cima.**

Um Monkeytype pessoal, com o seu próprio conteúdo.

![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![CodeMirror](https://img.shields.io/badge/CodeMirror_6-vim-D30707)
![Docker](https://img.shields.io/badge/Docker-compose-2496ED?logo=docker&logoColor=white)
![Sem build](https://img.shields.io/badge/front-sem_build-e2b714)

</div>

---

## ✨ O que é

App web de **um usuário só**. Os arquivos ficam organizados em pastas, e cada arquivo tem dois modos:

| Modo | O que acontece |
|---|---|
| **edição** | editor CodeMirror com vim (`hjkl`, `i`, `dd`, `yy`, `p`, `u`, `:w`...) |
| **reminder** | o texto aparece cinza e você digita por cima: acerto fica branco, erro fica vermelho. Espaços, indentação e quebras de linha são pulados sozinhos |

Nada de estatística, progresso ou "concluído". É só digitar.

## 🎹 Atalhos

| Tecla | Ação |
|---|---|
| `Ctrl+E` | alterna edição ↔ reminder |
| `Ctrl+B` | esconde/mostra a área do arquivo |
| `Ctrl+J` / `Ctrl+K` | desce/sobe no painel de arquivos (o foco vai pro painel) |
| `Enter` no painel | pasta: abre/fecha · arquivo: abre |
| `Ctrl+O` ou `n` no painel | cria arquivo (`a/b/c.txt`) ou pasta (`a/b/`), criando o caminho inteiro |
| `r` no painel | renomeia/move |
| `Ctrl+Delete` ou `d` no painel | apaga (com confirmação) |
| `↑` / `↓` no reminder | pula para o primeiro caractere da linha de cima/baixo |
| `Backspace` no reminder | volta um caractere |

Os atalhos ficam nos objetos `CTRL` e `PANEL`, no topo do script de `static/index.html`.

## 🧱 Como é feito

```
supra/
├── app.py              # back inteiro: login, árvore, ler/salvar, criar/mover/apagar
├── static/
│   ├── index.html      # painel + editor + modo reminder (HTML/CSS/JS puro)
│   └── login.html
├── data/               # os arquivos do usuário (volume, fora do git)
├── Dockerfile          # imagem uv + python 3.13 alpine
├── compose.yaml        # publica só em 127.0.0.1:8083
├── pyproject.toml / uv.lock
└── .env                # senha e segredo (fora do git; ver .env.example)
```

- **Sem banco:** o sistema de arquivos é o banco. Pasta é diretório, arquivo é arquivo de texto, tudo dentro de `data/`.
- **Sem build no front:** CodeMirror 6 e `@replit/codemirror-vim` vêm do `esm.sh`.
- **Login:** uma senha (`SUPRA_PASSWORD`). O cookie `s` é um HMAC da senha com `SUPRA_SECRET`, então trocar a senha desloga todo mundo.
- **URLs são caminhos:** `/pasta/arquivo.py` abre o arquivo. Qualquer rota que não seja `/login` ou `/api/*` devolve a mesma página.

### API

| Rota | Faz |
|---|---|
| `GET/POST /login`, `POST /logout` | sessão |
| `GET /api/tree` | lista plana e ordenada; pasta termina com `/` |
| `GET /api/file?path=` | conteúdo em texto puro |
| `PUT /api/file?path=` | salva o corpo da requisição |
| `POST /api/fs` | `{"action": "new" \| "mv" \| "rm", "path": "...", "to": "..."}` |

Qualquer caminho que tente sair de `data/` (`..`) recebe `400`.

## 🚀 Subir do zero

Pré-requisitos no servidor: Docker com o plugin compose e o Caddy rodando no host como reverse proxy.

```bash
git clone https://github.com/luiz-nast/supra.git
cd supra
cp .env.example .env        # defina SUPRA_PASSWORD e um SUPRA_SECRET aleatório
mkdir -p data
docker compose up -d --build
```

Para gerar um segredo aleatório:

```bash
head -c 32 /dev/urandom | base64
```

Bloco no `/etc/caddy/Caddyfile`:

```caddy
supra.premiumlts.com.br {
reverse_proxy 127.0.0.1:8083
}
```

```bash
caddy reload --config /etc/caddy/Caddyfile
```

DNS: registro **A** `supra` apontando para o IP do servidor.

### Checklist pós-deploy

- [ ] `curl -I http://127.0.0.1:8083/` responde `307` para `/login`
- [ ] `https://supra.premiumlts.com.br` abre com HTTPS válido
- [ ] login funciona com a senha do `.env`
- [ ] conteúdo antigo restaurado em `data/` (se houver backup)

## 🔧 Manutenção

| Situação | Comando |
|---|---|
| mudou código ou `static/` | `docker compose up -d --build` |
| mudou o `.env` | `docker compose up -d` (**não** use `restart`: ele não relê o `.env`) |
| logs | `docker compose logs -f` |
| backup do conteúdo | copiar a pasta `data/` |

## 🎨 Cores

Paleta *serika dark* do Monkeytype, em variáveis CSS no `:root` de `index.html`:

| | |
|---|---|
| fundo | `#323437` |
| não digitado | `#646669` |
| certo / texto | `#d1d0c5` |
| erro | `#ca4754` |
| cursor | `#e2b714` |
