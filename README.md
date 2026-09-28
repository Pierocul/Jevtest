# Demos de Jev (TypeSafe)

Cinco demos web que muestran cómo Jev responde **muchas preguntas a la vez**:

| Página | Qué hace | Preguntas por llamada |
|---|---|---|
| `/` 📨 Triaje | Clasifica mensajes de clientes | 3 |
| `/examen` 📝 Exámenes | Corrige a toda una clase en paralelo | ~15 por alumno |
| `/cv` 👤 CV vs oferta | Revisa cada requisito de la oferta | 14 |
| `/pelicula` 🎬 Adivina la peli | Juego de pistas sobre ~70 películas | 9 |
| `/ensayo` ✍️ Ensayos | Rúbrica de 6 aspectos + chequeos | 12 |

Cada página trae ejemplos listos; en [EJEMPLOS.md](EJEMPLOS.md) hay más textos
para copiar y pegar. El panel derecho muestra exactamente qué se envió a Jev y
qué respondió. El código de cada demo está en `demos/`.

---

# Demo de terminal: clasificar mensajes de clientes

Usa el modelo **Jev** de [TypeSafe](https://docs.typesafe.ai) (SDK oficial `typesafe-sdk`).
Para cada mensaje hace **una sola llamada** con tres preguntas:

| Pregunta | Tipo TypeSafe | Qué devuelve |
|---|---|---|
| ¿Es consulta, queja, venta u otro? | `Choice` | la opción elegida, probabilidad de cada opción y confianza |
| ¿Es spam? | `Noul` | probabilidad de que sea spam (0 a 1) |
| ¿Qué tan urgente es? | `Score` | nivel baja/media/alta, probabilidades y confianza |

## Cómo correrlo

1. Consigue tu clave en https://console.typesafe.ai/ y guárdala:
   ```sh
   export TYPESAFE_API_KEY="tu-clave"
   ```
2. Instala las dependencias (Python 3.10 o superior):
   ```sh
   python3 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   ```
3. Ejecuta la demo:
   ```sh
   .venv/bin/python demo.py
   ```

Verás una tabla con los 5 mensajes de ejemplo. Para probar los tuyos, edita la lista
`MENSAJES` en `demo.py`.

## Cómo leer los resultados

- **Probabilidad**: qué tan probable es cada respuesta posible.
- **Confianza**: qué tan seguro está el modelo de su respuesta. Si es baja
  (por ejemplo, menos de 60 %), conviene que lo revise una persona.
- Jev funciona mejor en inglés; en español va bien, pero vigila la confianza.

## Versión web (para probar desde el celular)

`app.py` sirve todas las demos.
La clave de TypeSafe se queda en el servidor; el navegador nunca la ve.

Correrla en tu computadora:
```sh
.venv/bin/uvicorn app:app --port 8000
```
y abre http://localhost:8000

### Probarla con GitHub Codespaces (sin instalar nada)

GitHub Pages no sirve: TypeSafe no acepta llamadas desde páginas estáticas.
Codespaces sí, porque ejecuta el servidor en la nube de GitHub.

1. En github.com abre el repo y elige la rama con este código.
2. Toca **Code → Codespaces → Create codespace on …**.
3. GitHub te pide `TYPESAFE_API_KEY`: pega tu clave (queda guardada como
   secreto, no en el código).
4. Espera 1-2 minutos: se instala todo y la web arranca sola. Si no se abre,
   ve a la pestaña **Ports** y toca el globo 🌐 del puerto 8000.

El enlace solo lo puedes abrir tú (con tu sesión de GitHub). Cuando termines,
detén el codespace para no gastar tus horas gratis.

### Publicarla gratis en Render (se puede hacer desde el celular)

1. Entra en https://render.com e inicia sesión con tu cuenta de GitHub.
2. Toca **New → Blueprint** y elige el repo `jevtest` (y la rama con este código).
3. Render lee `render.yaml` y te pide dos valores:
   - `TYPESAFE_API_KEY`: tu clave de TypeSafe.
   - `CODIGO_ACCESO`: una palabra secreta. La página te la pedirá la primera vez,
     así nadie más gasta tu saldo. Si la dejas vacía, la página queda abierta.
4. Toca **Apply** y espera unos minutos. Render te da una dirección
   `https://jev-triaje-xxxx.onrender.com`: ábrela en el celular.

En el plan gratis la web "se duerme" si nadie la usa; la primera visita tarda
unos 30-60 segundos en despertar.
