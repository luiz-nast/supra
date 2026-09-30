import hashlib
import hmac
import os
import shutil
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import FileResponse, PlainTextResponse, RedirectResponse

DATA = Path("data").resolve()
PASSWORD = os.environ["SUPRA_PASSWORD"]
# o cookie é só um hash da senha: trocou a senha, todo mundo é deslogado
TOKEN = hmac.new(os.environ["SUPRA_SECRET"].encode(), PASSWORD.encode(), hashlib.sha256).hexdigest()

app = FastAPI()


@app.middleware("http")
async def auth(request: Request, call_next):
    if request.url.path == "/login" or hmac.compare_digest(request.cookies.get("s", ""), TOKEN):
        return await call_next(request)
    if request.url.path.startswith("/api/"):
        return PlainTextResponse("faça login", 401)
    return RedirectResponse("/login")


def safe(path: str) -> Path:
    p = (DATA / path.strip("/")).resolve()
    if p == DATA or not p.is_relative_to(DATA):
        raise HTTPException(400, "caminho inválido")
    return p


@app.get("/login")
def login_page():
    return FileResponse("static/login.html")


@app.post("/login")
def login(password: str = Form()):
    if not hmac.compare_digest(password, PASSWORD):
        return RedirectResponse("/login?erro", 303)
    r = RedirectResponse("/", 303)
    r.set_cookie("s", TOKEN, max_age=60 * 60 * 24 * 365, httponly=True, secure=True, samesite="lax")
    return r


@app.post("/logout")
def logout():
    r = RedirectResponse("/login", 303)
    r.delete_cookie("s")
    return r


@app.get("/api/tree")
def tree():
    # lista plana; pasta termina com "/"
    return sorted(str(p.relative_to(DATA)) + ("/" if p.is_dir() else "") for p in DATA.rglob("*"))


@app.get("/api/file")
def read(path: str):
    return PlainTextResponse(safe(path).read_text())


@app.put("/api/file")
async def write(path: str, request: Request):
    safe(path).write_text((await request.body()).decode())


@app.post("/api/fs")
def fs(body: dict):
    p = safe(body["path"])
    match body["action"]:
        case "new":  # "a/b/" cria pasta, "a/b" cria arquivo
            if body["path"].endswith("/"):
                p.mkdir(parents=True)
            else:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.touch(exist_ok=False)
        case "mv":
            to = safe(body["to"])
            to.parent.mkdir(parents=True, exist_ok=True)
            p.rename(to)
        case "rm":
            shutil.rmtree(p) if p.is_dir() else p.unlink()


# qualquer outro caminho (/, /pasta/arquivo) é a mesma página; o JS lê a URL
@app.get("/{path:path}")
def page(path: str):
    return FileResponse("static/index.html")
