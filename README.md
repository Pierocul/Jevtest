# Demo: clasificar mensajes de clientes con Jev

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

`app.py` sirve una página donde escribes mensajes y ves la clasificación al momento.
La clave de TypeSafe se queda en el servidor; el navegador nunca la ve.

Correrla en tu computadora:
```sh
.venv/bin/uvicorn app:app --port 8000
```
y abre http://localhost:8000

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
