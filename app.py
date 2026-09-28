"""Web de la demo: la página manda el mensaje y este servidor pregunta a Jev.

La clave TYPESAFE_API_KEY se queda en el servidor; el navegador nunca la ve.
Si defines CODIGO_ACCESO, la página pide ese código antes de analizar.
"""

import os
import secrets
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typesafe_sdk import TypeSafeClient

from demo import MENSAJES, analizar

CODIGO_ACCESO = os.environ.get("CODIGO_ACCESO", "")
PAGINA = (Path(__file__).parent / "static" / "index.html").read_text(encoding="utf-8")

app = FastAPI(title="Jev · Triaje de mensajes")
client = TypeSafeClient()


class Entrada(BaseModel):
    mensaje: str = Field(min_length=1, max_length=1000)


@app.get("/", response_class=HTMLResponse)
def pagina() -> str:
    return PAGINA


@app.get("/api/config")
def config() -> dict:
    return {"pide_codigo": bool(CODIGO_ACCESO), "ejemplos": MENSAJES}


@app.post("/api/analizar")
def analizar_mensaje(entrada: Entrada, x_codigo: str = Header(default="")) -> dict:
    if CODIGO_ACCESO and not secrets.compare_digest(x_codigo, CODIGO_ACCESO):
        raise HTTPException(status_code=401, detail="Código de acceso incorrecto")
    return analizar(client, entrada.mensaje.strip())
