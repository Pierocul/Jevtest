"""CV vs oferta: cada requisito es un Noul; todo va en una sola llamada."""

from pydantic import BaseModel, Field
from typesafe_sdk import AsyncTypeSafeClient, Choice, Noul, Score

from .comun import nivel_mas_probable, preguntar


class Entrada(BaseModel):
    oferta: str = Field(min_length=1, max_length=3000)
    obligatorios: list[str] = Field(max_length=20)
    deseables: list[str] = Field(max_length=20)
    cv: str = Field(min_length=1, max_length=8000)


ENCAJE = [
    "No encaja: su experiencia es de otra área",
    "Encaje bajo: algo relacionado, pero le falta mucho",
    "Buen encaje: cumple lo principal con algunas carencias",
    "Encaje excelente: parece hecho para el puesto",
]

SENIORITY = {
    "junior": "Poca experiencia profesional; necesita guía",
    "semi_senior": "Trabaja con autonomía en tareas normales",
    "senior": "Mucha experiencia; resuelve problemas complejos y decide la técnica",
    "lead": "Además lidera equipos o proyectos",
}

ALERTAS = {
    "cambios_frecuentes": "¿El `cv` muestra varios trabajos que duraron menos de un año cada uno?",
    "otra_area": (
        "¿La experiencia principal del `cv` es de un área distinta a la del puesto "
        "de la `oferta` (por ejemplo diseño, ventas o soporte)?"
    ),
    "cv_descuidado": "¿El `cv` tiene faltas de ortografía o está desordenado?",
}


def limpiar(lista: list[str]) -> list[str]:
    return [x.strip() for x in lista if x.strip()]


async def analizar(client: AsyncTypeSafeClient, datos: Entrada) -> dict:
    obligatorios, deseables = limpiar(datos.obligatorios), limpiar(datos.deseables)
    requisitos = [("obligatorio", r) for r in obligatorios] + [("deseable", r) for r in deseables]

    preguntas: dict = {
        f"req_{i}": Noul(instructions=f"¿El `cv` demuestra que el candidato cumple este requisito: «{texto}»?")
        for i, (_, texto) in enumerate(requisitos)
    }
    preguntas["encaje"] = Score(
        instructions="¿Qué tan bien encaja el `cv` con el puesto de la `oferta`?", criteria=ENCAJE
    )
    preguntas["seniority"] = Choice(
        instructions="¿Qué nivel de experiencia (seniority) muestra el `cv`?", criteria=SENIORITY
    )
    for k, texto in ALERTAS.items():
        preguntas[f"alerta_{k}"] = Noul(instructions=texto)

    r, llamada = await preguntar(client, {"oferta": datos.oferta, "cv": datos.cv}, preguntas)

    reqs = [
        {"tipo": tipo, "texto": texto, "prob": r.nouls[f"req_{i}"].noul}
        for i, (tipo, texto) in enumerate(requisitos)
    ]
    prom = lambda xs: sum(xs) / len(xs) if xs else 1.0  # noqa: E731
    p_obl = [x["prob"] for x in reqs if x["tipo"] == "obligatorio"]
    p_des = [x["prob"] for x in reqs if x["tipo"] == "deseable"]
    # La cuenta la hace el código, no Jev: 70% obligatorios, 30% deseables.
    puntaje = round(100 * (0.7 * prom(p_obl) + 0.3 * prom(p_des)))
    faltan = [x["texto"] for x in reqs if x["tipo"] == "obligatorio" and x["prob"] < 0.5]
    dudosos = [x["texto"] for x in reqs if 0.3 < x["prob"] < 0.7]

    enc = r.scores["encaje"]
    sen = r.choices["seniority"]
    alertas = {k: r.nouls[f"alerta_{k}"].noul for k in ALERTAS}
    alertas_altas = [k for k, v in alertas.items() if v >= 0.7]
    if faltan:
        veredicto = ("bad", f"❌ Descartar: no cumple {len(faltan)} requisito(s) obligatorio(s)")
    elif dudosos or enc.confidence < 0.6:
        veredicto = ("warn", "⚠ Revisar a mano: hay requisitos dudosos")
    elif alertas_altas:
        veredicto = ("warn", "⚠ Buen perfil, pero con alertas: revisar a mano")
    elif puntaje >= 75:
        veredicto = ("ok", "✓ Pasar a entrevista")
    else:
        veredicto = ("warn", "≈ Cumple lo mínimo: entrevista opcional")

    return {
        "requisitos": reqs,
        "puntaje": puntaje,
        "faltan": faltan,
        "veredicto": veredicto,
        "encaje": {"nivel": enc.legend[nivel_mas_probable(enc)], "score": enc.score,
                   "max": len(ENCAJE) - 1, "confianza": enc.confidence},
        "seniority": {"valor": sen.choice, "probs": sen.probabilities, "confianza": sen.confidence},
        "alertas": alertas,
        "llamada": llamada,
    }
