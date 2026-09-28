"""Triaje de mensajes de clientes (misma lógica que demo.py, en versión web)."""

from pydantic import BaseModel, Field
from typesafe_sdk import AsyncTypeSafeClient

from demo import PREGUNTAS, resumir

from .comun import preguntar


class Entrada(BaseModel):
    mensaje: str = Field(min_length=1, max_length=1000)


async def analizar(client: AsyncTypeSafeClient, datos: Entrada) -> dict:
    mensaje = datos.mensaje.strip()
    r, llamada = await preguntar(client, {"mensaje_del_cliente": mensaje}, PREGUNTAS)
    return {**resumir(mensaje, r), "llamada": llamada}
