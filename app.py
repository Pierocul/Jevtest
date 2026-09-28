"""Web de las demos: las páginas mandan los datos y este servidor pregunta a Jev.

La clave TYPESAFE_API_KEY se queda en el servidor; el navegador nunca la ve.
Si defines CODIGO_ACCESO, las páginas piden ese código antes de llamar a Jev.
"""

import json
import os
import secrets
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from typesafe_sdk import AsyncTypeSafeClient, TypeSafeError

from demo import MENSAJES
from demos import cv, ensayo, examen, pelicula, triaje

RAIZ = Path(__file__).parent
ESTATICOS = RAIZ / "static"
CODIGO_ACCESO = os.environ.get("CODIGO_ACCESO", "")
DEMOS = {"triaje": triaje, "examen": examen, "cv": cv, "pelicula": pelicula, "ensayo": ensayo}
PAGINAS = {"": "index.html", **{k: f"{k}.html" for k in DEMOS if k != "triaje"}}

cliente: AsyncTypeSafeClient


@asynccontextmanager
async def ciclo_de_vida(_: FastAPI):
    global cliente
    async with AsyncTypeSafeClient() as cliente:
        yield


app = FastAPI(title="Jev · demos", lifespan=ciclo_de_vida)
app.mount("/static", StaticFiles(directory=ESTATICOS), name="static")


@app.get("/api/ejemplos/{nombre}")
def ejemplos(nombre: str) -> dict:
    if nombre == "triaje":
        return {"mensajes": MENSAJES}
    if nombre == "pelicula":
        datos = json.loads((RAIZ / "ejemplos" / "pelicula.json").read_text(encoding="utf-8"))
        return {**datos, "catalogo": pelicula.CATALOGO}
    if nombre not in DEMOS:
        raise HTTPException(status_code=404, detail="No existe ese ejemplo")
    return json.loads((RAIZ / "ejemplos" / f"{nombre}.json").read_text(encoding="utf-8"))


@app.post("/api/{nombre}")
async def analizar(nombre: str, request: Request, x_codigo: str = Header(default="")) -> dict:
    if nombre not in DEMOS:
        raise HTTPException(status_code=404, detail="No existe esa demo")
    if CODIGO_ACCESO and not secrets.compare_digest(x_codigo, CODIGO_ACCESO):
        raise HTTPException(status_code=401, detail="Código de acceso incorrecto")
    modulo = DEMOS[nombre]
    try:
        datos = modulo.Entrada.model_validate(await request.json())
    except (ValidationError, ValueError) as e:
        raise HTTPException(status_code=422, detail=f"Datos no válidos: {e}") from e
    try:
        return await modulo.analizar(cliente, datos)
    except TypeSafeError as e:
        raise HTTPException(status_code=502, detail=f"Error de TypeSafe: {e}") from e


@app.get("/{pagina}")
@app.get("/", include_in_schema=False)
def pagina(pagina: str = "") -> FileResponse:
    if pagina not in PAGINAS:
        raise HTTPException(status_code=404, detail="Página no encontrada")
    return FileResponse(ESTATICOS / PAGINAS[pagina])
