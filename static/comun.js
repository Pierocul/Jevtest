// Funciones compartidas por todas las demos.

const DEMOS = [
  ["/", "📨 Triaje"],
  ["/examen", "📝 Exámenes"],
  ["/cv", "👤 CV vs oferta"],
  ["/pelicula", "🎬 Adivina la peli"],
  ["/ensayo", "✍️ Ensayos"],
];

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

function metricas({ llamadas = 1, preguntas, ms }) {
  const txt = llamadas > 1
    ? `⚡ ${llamadas} llamadas en paralelo · ${preguntas} preguntas · ${seg(ms)}`
    : `⚡ 1 llamada · ${preguntas} preguntas a la vez · ${seg(ms)}`;
  return el("div", "metricas", txt);
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
