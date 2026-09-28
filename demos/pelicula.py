"""Adivina la película: un Choice sobre el catálogo + Nouls sobre lo que dicen las pistas."""

from pydantic import BaseModel, Field
from typesafe_sdk import AsyncTypeSafeClient, Choice, Noul

from .comun import preguntar

# Hay "parejas trampa" a propósito (Coco / El libro de la vida, Matrix / Origen...).
CATALOGO = [
    "Titanic (1997)", "Pearl Harbor (2001)", "Avatar (2009)", "Matrix (1999)",
    "Origen (2010)", "Blade Runner (1982)", "Interestelar (2014)", "Gravity (2013)",
    "Volver al futuro (1985)", "Jurassic Park (1993)", "Tiburón (1975)", "E.T. (1982)",
    "Star Wars: Una nueva esperanza (1977)", "El señor de los anillos: La comunidad del anillo (2001)",
    "Harry Potter y la piedra filosofal (2001)", "El padrino (1972)", "Pulp Fiction (1994)",
    "Forrest Gump (1994)", "El rey león (1994)", "Toy Story (1995)", "Buscando a Nemo (2003)",
    "Shrek (2001)", "Up (2009)", "Intensamente (2015)", "Coco (2017)", "Encanto (2021)",
    "El libro de la vida (2014)", "Frozen (2013)", "Ratatouille (2007)", "Wall-E (2008)",
    "El viaje de Chihiro (2001)", "Mi vecino Totoro (1988)", "Los increíbles (2004)",
    "Vengadores: Endgame (2019)", "El caballero oscuro (2008)", "Joker (2019)",
    "Spider-Man: Un nuevo universo (2018)", "Black Panther (2018)", "Parásitos (2019)",
    "El laberinto del fauno (2006)", "El orfanato (2007)", "La forma del agua (2017)",
    "Roma (2018)", "Y tu mamá también (2001)", "Amores perros (2000)", "Relatos salvajes (2014)",
    "El secreto de sus ojos (2009)", "Nueve reinas (2000)", "La sociedad de la nieve (2023)",
    "Mar adentro (2004)", "Todo sobre mi madre (1999)", "Campeones (2018)",
    "Ocho apellidos vascos (2014)", "El exorcista (1973)", "El resplandor (1980)",
    "It (2017)", "Scream (1996)", "Alien (1979)", "La La Land (2016)", "Mamma Mia! (2008)",
    "Gladiador (2000)", "Braveheart (1995)", "Piratas del Caribe: La maldición del Perla Negra (2003)",
    "Indiana Jones: En busca del arca perdida (1981)", "Mad Max: Furia en la carretera (2015)",
    "Rápidos y furiosos (2001)", "El club de la pelea (1999)", "Barbie (2023)", "Oppenheimer (2023)",
    "Náufrago (2000)", "Solo en casa (1990)", "El show de Truman (1998)", "Los juegos del hambre (2012)",
]
NINGUNA = "Ninguna de estas películas"

PISTAS_SOBRE = {
    "animada": "¿Las `pistas` indican que es una película animada?",
    "en_espanol": "¿Las `pistas` indican que es una película en español?",
    "antes_2000": "¿Las `pistas` indican que la película se estrenó antes del año 2000?",
    "para_ninos": "¿Las `pistas` indican que es una película para niños o para toda la familia?",
    "miedo": "¿Las `pistas` indican que es una película de terror o de suspenso?",
    "ciencia_ficcion": "¿Las `pistas` indican que es de ciencia ficción o fantasía?",
    "romance": "¿Las `pistas` indican que hay una historia de amor importante?",
    "basada_en_hechos": "¿Las `pistas` indican que está basada en hechos reales?",
}


class Entrada(BaseModel):
    pistas: list[str] = Field(min_length=1, max_length=15)


async def analizar(client: AsyncTypeSafeClient, datos: Entrada) -> dict:
    pistas = [p.strip() for p in datos.pistas if p.strip()][:15]
    preguntas: dict = {
        "pelicula": Choice(
            instructions="¿De qué película hablan las `pistas`?",
            criteria={**{t: None for t in CATALOGO}, NINGUNA: "La película de las pistas no está en la lista"},
        ),
        **{f"pista_{k}": Noul(instructions=q) for k, q in PISTAS_SOBRE.items()},
    }
    r, llamada = await preguntar(client, {"pistas": pistas}, preguntas)

    c = r.choices["pelicula"]
    top = sorted(c.probabilities.items(), key=lambda kv: kv[1], reverse=True)[:5]
    mejor, prob = top[0]
    if mejor == NINGUNA and prob > 0.5 and c.confidence >= 0.7:
        estado = ("warn", "🤔 Creo que no está en mi catálogo")
    elif prob >= 0.7 and c.confidence >= 0.7:
        estado = ("ok", f"🎬 ¡Es {mejor}!")
    elif prob >= 0.4 and mejor != NINGUNA:
        estado = ("warn", f"🤏 Casi seguro: ¿{mejor}? Dame otra pista")
    else:
        estado = ("muted", "🧐 Ni idea todavía… dame otra pista")

    return {
        "top": [{"titulo": t, "prob": p} for t, p in top],
        "confianza": c.confidence,
        "estado": estado,
        "inferencias": {k: r.nouls[f"pista_{k}"].noul for k in PISTAS_SOBRE},
        "catalogo": len(CATALOGO),
        "llamada": llamada,
    }
