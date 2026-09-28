// Funciones compartidas por todas las demos.

const DEMOS = [
  ["/", "📨 Triaje"],
  ["/examen", "📝 Exámenes"],
  ["/cv", "👤 CV vs oferta"],
  ["/pelicula", "🎬 Adivina la peli"],
  ["/ensayo", "✍️ Ensayos"],
  ["/ayuda", "ℹ️ Cómo usar"],
];

// Instrucciones cortas de cada demo (se muestran en «¿Cómo se usa?»)
const AYUDA = {
  "/": [
    "Toca «▶ Probar ejemplos» para analizar 5 mensajes de clientes, o escribe el tuyo abajo y toca «Enviar».",
    "Cada mensaje sale con su tipo, la probabilidad de spam y la urgencia.",
    "La línea de color es la decisión: a qué equipo mandarlo, revisarlo a mano o descartarlo.",
  ],
  "/examen": [
    "Ya hay un examen de ciencias y 5 alumnos cargados. Toca «▶ Corregir toda la clase».",
    "Cada alumno sale con su nota y cada pregunta en verde (bien), amarillo (a medias) o rojo (mal). El «?» significa que Jev duda.",
    "Toca «＋ Añadir alumno» para escribir tus propias respuestas y ver cómo las corrige.",
  ],
  "/cv": [
    "Elige un CV de ejemplo y toca «▶ Analizar este CV», o «⚡ Los 4 en paralelo» para ver un ranking.",
    "Cada requisito sale con ✅ (lo cumple), ❌ (no) o ❓ (duda) y su probabilidad.",
    "Puedes cambiar la oferta y los requisitos, o pegar tu propio CV con «✏️ Pegar el mío».",
  ],
  "/pelicula": [
    "Piensa en una película y escribe una pista corta. Toca «Pista».",
    "Sigue dando pistas de a una: verás cómo cambian las probabilidades del Top 5.",
    "Toca «🎲 Ejemplo» para ver una partida automática, o «↺ Nueva» para empezar otra.",
  ],
  "/ensayo": [
    "Elige un ensayo de ejemplo y toca «▶ Corregir ensayo», o escribe el tuyo con «✏️ Escribir el mío».",
    "Sale una nota de 0 a 10 y cada aspecto de la rúbrica con su nivel y un consejo si sale bajo.",
    "Puedes cambiar la consigna por cualquier otro tema.",
  ],
};

async function compartir(boton) {
  const datos = { title: "Demos de Jev", text: "Mira lo que hace Jev, el modelo de TypeSafe:", url: location.origin + location.pathname };
  try {
    if (navigator.share) return await navigator.share(datos);
    await navigator.clipboard.writeText(datos.url);
    boton.textContent = "✓ Enlace copiado";
  } catch {}
}

function botonCompartir() {
  const b = el("button", "ghost", "🔗 Compartir esta página");
  b.onclick = () => compartir(b);
  return b;
}

const $ = (s, raiz = document) => raiz.querySelector(s);
const pct = (x) => Math.round(x * 100) + "%";
const seg = (ms) => (ms < 1000 ? `${ms} ms` : `${(ms / 1000).toFixed(1)} s`);

function el(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text != null) e.textContent = text;
  return e;
}

function tag(label, valor, cls = "") {
  const s = el("span", "tag " + cls, label ? label + " " : "");
  s.append(el("b", null, valor));
  return s;
}

function barras(filas) {
  // filas: [[etiqueta, valor 0..1, texto opcional]]
  const b = el("div", "bars");
  for (const [etiqueta, v, texto] of filas) {
    const barra = el("div", "bar"), i = el("i");
    i.style.width = pct(v);
    barra.append(i);
    b.append(el("span", null, etiqueta), barra, el("span", null, texto ?? pct(v)));
  }
  return b;
}

const dolares = (c) => "$" + (c >= 0.01 ? c.toFixed(2) : c.toPrecision(2));
const miles = (n) => n.toLocaleString("es");

function metricas({ llamadas = 1, preguntas, ms, tokens, costo }) {
  const txt = llamadas > 1
    ? `⚡ ${llamadas} llamadas en paralelo · ${preguntas} preguntas · ${seg(ms)}`
    : `⚡ 1 llamada · ${preguntas} preguntas a la vez · ${seg(ms)}`;
  const m = el("div", "metricas", txt);
  if (tokens) m.append(el("div", "muted", `${miles(tokens)} tokens · costó ${dolares(costo)}`));
  return m;
}

// Menú superior
(function menu() {
  const header = $("header");
  const logo = el("a", "logo");
  logo.href = "/";
  logo.append("jev", el("span", null, "/demos"));
  const nav = el("nav");
  for (const [href, texto] of DEMOS) {
    const a = el("a", location.pathname === href ? "on" : "", texto);
    a.href = href;
    nav.append(a);
  }
  header.append(logo, nav);
  nav.querySelector(".on")?.scrollIntoView({ inline: "center", block: "nearest" });

  const pasos = AYUDA[location.pathname];
  const lead = $(".lead");
  if (pasos && lead) {
    const d = el("details", "ayuda");
    const ol = el("ol", "lista");
    for (const p of pasos) ol.append(el("li", null, p));
    const pie = el("div", "fila");
    pie.style.marginTop = "10px";
    const mas = el("a", null, "Más ayuda →");
    mas.href = "/ayuda";
    pie.append(botonCompartir(), mas);
    d.append(el("summary", null, "❓ ¿Cómo se usa?"), ol, pie);
    lead.after(d);
  }
})();

// Llamadas al servidor (con código de acceso opcional)
let codigo = "";
try { codigo = localStorage.getItem("codigo") || ""; } catch {}

async function api(ruta, datos) {
  const res = await fetch(ruta, {
    method: datos ? "POST" : "GET",
    headers: { "Content-Type": "application/json", "X-Codigo": codigo },
    body: datos ? JSON.stringify(datos) : undefined,
  });
  if (res.status === 401) {
    codigo = prompt("Código de acceso:") || "";
    try { localStorage.setItem("codigo", codigo); } catch {}
    if (codigo) return api(ruta, datos);
    throw new Error("Hace falta el código de acceso");
  }
  if (!res.ok) {
    const cuerpo = await res.json().catch(() => ({}));
    throw new Error(typeof cuerpo.detail === "string" ? cuerpo.detail : "Error " + res.status);
  }
  return res.json();
}

// Panel derecho: lo que se envió a Jev y lo que respondió
function panelJSON(contenedor) {
  contenedor.classList.add("panel", "sticky");
  const tabs = el("div", "tabs");
  const pres = {
    enviado: el("pre", null, "// Aquí verás todas las preguntas que se mandan a Jev en UNA llamada."),
    respuesta: el("pre", null, "// Aquí verás la respuesta de Jev."),
  };
  const nombres = { enviado: "preguntas.json", respuesta: "respuesta.json" };
  for (const k of Object.keys(pres)) {
    const b = el("button", "tab", nombres[k]);
    b.onclick = () => abrir(k);
    b.dataset.tab = k;
    tabs.append(b);
  }
  pres.respuesta.hidden = true;
  const info = el("div", "panel-body");
  info.hidden = true;
  contenedor.append(info, tabs, pres.enviado, pres.respuesta);
  function abrir(k) {
    tabs.querySelectorAll(".tab").forEach((t) => t.classList.toggle("on", t.dataset.tab === k));
    for (const [n, p] of Object.entries(pres)) p.hidden = n !== k;
  }
  abrir("enviado");
  return {
    mostrar(llamada, titulo) {
      pres.enviado.textContent = JSON.stringify(llamada.enviado, null, 2);
      pres.respuesta.textContent = JSON.stringify(llamada.respuesta, null, 2);
      info.replaceChildren(metricas(llamada));
      if (titulo) info.prepend(el("div", "tag", titulo));
      info.hidden = false;
    },
  };
}

function marcar(card) {
  document.querySelectorAll(".card.sel").forEach((c) => c.classList.remove("sel"));
  card.classList.add("sel");
}
