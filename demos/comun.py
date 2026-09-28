"""Utilidades compartidas: una llamada a Jev medida, lista para mostrar en la web."""

import time
from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

from typesafe_sdk import AsyncTypeSafeClient, SystemOneResponse

MODELO = "jev-latest"
# Precio de Jev 1.13 (docs.typesafe.ai/models): solo se cobran los tokens de entrada.
DOLARES_POR_MILLON = 0.042

# Uso acumulado desde que arrancó el servidor (se reinicia si el servidor se reinicia).
USO = {
    "desde": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "llamadas": 0,
    "preguntas": 0,
    "tokens_entrada": 0,
}


def costo(tokens: int) -> float:
    return tokens * DOLARES_POR_MILLON / 1_000_000


async def preguntar(
    client: AsyncTypeSafeClient, state: Any, preguntas: Mapping[str, Any]
) -> tuple[SystemOneResponse, dict]:
    """Hace UNA llamada con todas las preguntas y devuelve la respuesta y sus métricas."""
    inicio = time.perf_counter()
    r = await client.system_one(state=state, questions=preguntas, model=MODELO)
    ms = round((time.perf_counter() - inicio) * 1000)
    tokens = (r.usage.input_tokens or 0) if r.usage else 0
    USO["llamadas"] += 1
    USO["preguntas"] += len(preguntas)
    USO["tokens_entrada"] += tokens
    llamada = {
        "ms": ms,
        "preguntas": len(preguntas),
        "tokens": tokens,
        "costo": costo(tokens),
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
