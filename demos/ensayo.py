"""Corrector de ensayos: una rúbrica de 6 Scores + Nouls + Choices en una sola llamada."""

from pydantic import BaseModel, Field
from typesafe_sdk import AsyncTypeSafeClient, Choice, Noul, Score

from .comun import nivel_mas_probable, preguntar


class Entrada(BaseModel):
    consigna: str = Field(min_length=1, max_length=1000)
    texto: str = Field(min_length=1, max_length=8000)


# aspecto: (título, peso, pregunta, niveles de peor a mejor, consejo si sale bajo)
RUBRICA = {
    "consigna": (
        "Responde a la consigna", 2,
        "¿Qué tanto responde el `texto` a lo que pide la `consigna`?",
        ["No responde a la consigna", "La toca de forma superficial",
         "Responde a la consigna con algún desvío", "Responde de lleno a la consigna"],
        "Relee la consigna y asegúrate de responder exactamente lo que pide.",
    ),
    "tesis": (
        "Tesis clara", 2,
        "¿Qué tan clara es la postura u opinión principal del `texto`?",
        ["No hay una postura", "La postura se intuye pero no se dice",
         "La postura se dice pero de forma vaga", "La postura se dice con claridad desde el principio"],
        "Di tu opinión principal con claridad en el primer párrafo.",
    ),
    "argumentos": (
        "Argumentos y evidencias", 3,
        "¿Qué tan buenos son los argumentos del `texto` para defender su postura?",
        ["No da argumentos", "Argumentos débiles o solo opiniones",
         "Argumentos razonables con poco apoyo", "Argumentos sólidos con ejemplos o datos"],
        "Apoya cada argumento con un ejemplo, un dato o una experiencia concreta.",
    ),
    "estructura": (
        "Estructura y conectores", 2,
        "¿Qué tan bien organizado está el `texto` (párrafos, orden de ideas, conectores)?",
        ["Desordenado, sin párrafos", "Poco orden y casi sin conectores",
         "Ordenado, con algunos saltos", "Muy bien organizado y fácil de seguir"],
        "Usa párrafos (introducción, desarrollo, conclusión) y conectores como «además» o «por lo tanto».",
    ),
    "ortografia": (
        "Ortografía y gramática", 1,
        "¿Qué tan correcta es la ortografía y la gramática del `texto`?",
        ["Muchísimos errores", "Errores frecuentes", "Algunos errores", "Casi sin errores"],
        "Revisa tildes, mayúsculas y puntuación antes de entregar.",
    ),
    "vocabulario": (
        "Vocabulario y estilo", 1,
        "¿Qué tan rico y adecuado es el vocabulario del `texto`?",
        ["Muy pobre o inapropiado", "Repetitivo o demasiado informal",
         "Adecuado", "Variado y preciso"],
        "Evita repetir palabras y el lenguaje de chat; busca sinónimos.",
    ),
}

CHEQUEOS = {
    "introduccion": "¿El `texto` tiene una introducción que presenta el tema?",
    "conclusion": "¿El `texto` termina con una conclusión?",
    "ejemplos": "¿El `texto` usa ejemplos concretos?",
    "contraargumento": "¿El `texto` menciona y responde a una opinión contraria a la suya?",
}

POSTURA = {
    "a_favor": "Está a favor de lo que plantea la consigna",
    "en_contra": "Está en contra de lo que plantea la consigna",
    "matizada": "Ve ventajas y desventajas y propone un punto medio",
    "sin_postura": "No toma ninguna postura",
}

NIVEL_EDUCATIVO = {
    "primaria": "Escrito por un niño de primaria",
    "secundaria": "Escrito por un adolescente de secundaria",
    "universidad": "Escrito por un estudiante universitario",
    "profesional": "Escrito por un profesional o experto",
}


async def analizar(client: AsyncTypeSafeClient, datos: Entrada) -> dict:
    preguntas: dict = {
        f"rub_{k}": Score(instructions=q, criteria=niveles)
        for k, (_, _, q, niveles, _) in RUBRICA.items()
    }
    preguntas |= {f"chk_{k}": Noul(instructions=q) for k, q in CHEQUEOS.items()}
    preguntas["postura"] = Choice(instructions="¿Qué postura toma el `texto` sobre la `consigna`?", criteria=POSTURA)
    preguntas["nivel_educativo"] = Choice(
        instructions="¿Qué nivel educativo parece tener quien escribió el `texto`?", criteria=NIVEL_EDUCATIVO
    )
    r, llamada = await preguntar(client, {"consigna": datos.consigna, "texto": datos.texto}, preguntas)

    aspectos, suma, peso_total = [], 0.0, 0
    for k, (titulo, peso, _, niveles, consejo) in RUBRICA.items():
        s = r.scores[f"rub_{k}"]
        nivel = nivel_mas_probable(s)
        maximo = len(niveles) - 1
        suma += peso * nivel / maximo
        peso_total += peso
        aspectos.append({
            "titulo": titulo, "peso": peso, "nivel": nivel, "max": maximo,
            "texto_nivel": niveles[nivel], "confianza": s.confidence,
            "probs": [s.probabilities[i] for i in range(len(niveles))],
            "consejo": consejo if nivel <= 1 else "",
        })
    # La nota la calcula el código a partir de los niveles, con pesos fijos.
    nota = round(10 * suma / peso_total, 1)
    dudosos = [a["titulo"] for a in aspectos if a["confianza"] < 0.5]
    pos, niv = r.choices["postura"], r.choices["nivel_educativo"]

    return {
        "nota": nota,
        "aspectos": aspectos,
        "dudosos": dudosos,
        "chequeos": {k: r.nouls[f"chk_{k}"].noul for k in CHEQUEOS},
        "postura": {"valor": pos.choice, "prob": pos.probabilities[pos.choice], "confianza": pos.confidence},
        "nivel_educativo": {"valor": niv.choice, "prob": niv.probabilities[niv.choice], "confianza": niv.confidence},
        "llamada": llamada,
    }
