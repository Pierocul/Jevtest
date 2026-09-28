"""Utilidades compartidas: una llamada a Jev medida, lista para mostrar en la web."""

import time
from collections.abc import Mapping
from typing import Any

from typesafe_sdk import AsyncTypeSafeClient, SystemOneResponse

MODELO = "jev-latest"


async def preguntar(
    client: AsyncTypeSafeClient, state: Any, preguntas: Mapping[str, Any]
) -> tuple[SystemOneResponse, dict]:
    """Hace UNA llamada con todas las preguntas y devuelve la respuesta y sus métricas."""
    inicio = time.perf_counter()
    r = await client.system_one(state=state, questions=preguntas, model=MODELO)
    ms = round((time.perf_counter() - inicio) * 1000)
    llamada = {
        "ms": ms,
        "preguntas": len(preguntas),
        "modelo": r.model,
        "enviado": {
            "state": state,
            "questions": {k: q.model_dump(exclude_none=True) for k, q in preguntas.items()},
        },
        "respuesta": r.model_dump(mode="json"),
    }
    return r, llamada


def nivel_mas_probable(score) -> int:
    """Índice del nivel con más probabilidad (0 = el más bajo)."""
    return int(max(score.probabilities, key=score.probabilities.get))
