"""Demo: clasifica mensajes de clientes con Jev (TypeSafe System One).

Para cada mensaje se hace UNA sola llamada con tres preguntas:
  - tipo     (Choice): consulta, queja, venta u otro
  - spam     (Noul):   probabilidad de que sea spam
  - urgencia (Score):  baja, media o alta
"""

from typesafe_sdk import Choice, Noul, Score, SystemOneResponse, TypeSafeClient

MODELO = "jev-latest"

MENSAJES = [
    "Hola, ¿a qué hora abren la tienda el sábado?",
    "Llevo tres semanas esperando mi pedido y nadie me responde. Es una vergüenza.",
    "Quiero comprar 50 licencias para mi empresa, ¿me pueden enviar un presupuesto hoy?",
    "¡¡FELICIDADES!! Has ganado un iPhone gratis. Haz clic aquí para reclamar tu premio.",
    "URGENTE: me cobraron dos veces la factura y necesito que me devuelvan el dinero ya.",
]

PREGUNTAS = {
    "tipo": Choice(
        instructions="¿Qué tipo de mensaje de cliente es este?",
        criteria={
            "consulta": "Pregunta o pide información",
            "queja": "Expresa insatisfacción o reclama por un problema",
            "venta": "Quiere comprar o pide precio o presupuesto",
            "otro": "Ninguna de las anteriores",
        },
    ),
    "spam": Noul(
        instructions="¿Este mensaje es spam (publicidad no solicitada, estafa o phishing)?"
    ),
    "urgencia": Score(
        instructions="¿Qué tan urgente es atender este mensaje?",
        criteria=["baja", "media", "alta"],
    ),
}


def pct(x: float) -> str:
    return f"{x * 100:.0f}%"


def analizar(client: TypeSafeClient, mensaje: str) -> dict:
    r = client.system_one(
        state={"mensaje_del_cliente": mensaje}, questions=PREGUNTAS, model=MODELO
    )
    return resumir(mensaje, r)


def resumir(mensaje: str, r: SystemOneResponse) -> dict:
    tipo, spam, urg = r.choices["tipo"], r.nouls["spam"], r.scores["urgencia"]
    return {
        "mensaje": mensaje,
        "tipo": tipo.choice,
        "tipo_probs": tipo.probabilities,
        "tipo_conf": tipo.confidence,
        "spam": spam.noul,
        # Nivel más probable; el score es el promedio ponderado (0=baja, 2=alta).
        "urgencia": urg.legend[max(urg.probabilities, key=urg.probabilities.get)],
        "urgencia_score": urg.score,
        "urgencia_probs": {urg.legend[k]: v for k, v in urg.probabilities.items()},
        "urgencia_conf": urg.confidence,
        "modelo": r.model,
    }


def imprimir_tabla(filas: list[dict]) -> None:
    cab = ["#", "Mensaje", "Tipo", "Conf. tipo", "Spam", "Urgencia", "Conf. urg."]
    datos = [
        [
            str(i),
            f["mensaje"][:40] + ("…" if len(f["mensaje"]) > 40 else ""),
            f"{f['tipo']} ({pct(f['tipo_probs'][f['tipo']])})",
            pct(f["tipo_conf"]),
            pct(f["spam"]),
            f"{f['urgencia']} ({f['urgencia_score']:.2f}/2)",
            pct(f["urgencia_conf"]),
        ]
        for i, f in enumerate(filas, 1)
    ]
    anchos = [max(len(c), *(len(d[j]) for d in datos)) for j, c in enumerate(cab)]
    linea = "+-" + "-+-".join("-" * a for a in anchos) + "-+"
    print(linea)
    print("| " + " | ".join(c.ljust(a) for c, a in zip(cab, anchos)) + " |")
    print(linea)
    for d in datos:
        print("| " + " | ".join(c.ljust(a) for c, a in zip(d, anchos)) + " |")
    print(linea)

    print("\nDetalle de probabilidades:")
    for i, f in enumerate(filas, 1):
        tp = ", ".join(f"{k} {pct(v)}" for k, v in f["tipo_probs"].items())
        up = ", ".join(f"{k} {pct(v)}" for k, v in f["urgencia_probs"].items())
        print(f"  {i}. tipo: {tp} | urgencia: {up}")
    print(f"\nModelo que respondió: {filas[0]['modelo']}")


def main() -> None:
    with TypeSafeClient() as client:
        filas = [analizar(client, m) for m in MENSAJES]
    imprimir_tabla(filas)


if __name__ == "__main__":
    main()
