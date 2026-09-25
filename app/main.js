/* main.js: starts the viewer. Loads the data, loads every feature listed in modules.js, and shows
 * the view the address asks for ('#compare', '#driver/<id>', ...). */
import { loadAll } from "./core/data.js";
import { viewForPage } from "./core/registry.js";
import { readHash } from "./core/state.js";
import MODULES from "./modules.js";

const fetchJson = url => fetch(url, { cache: "no-cache" }).then(r => { if (!r.ok) throw new Error(`${url}: HTTP ${r.status}`); return r.json(); });

function route() {
  let where;
  try { where = readHash(); } catch (e) { location.hash = ""; return; }
  const view = viewForPage(where.page);
  if (view) view.show(where);
}

async function start() {
  const box = document.getElementById("app");
  try {
    await loadAll(fetchJson);
  } catch (e) {
    box.textContent = "";
    const err = document.createElement("div"); err.className = "err";
    err.textContent = `Couldn't load the database: ${e.message}. Make sure drivers.json sits next to index.html.`;
    box.appendChild(err);
    return;
  }
  const failed = [];
  for (const m of MODULES) {
    try { await import(m); } catch (e) { failed.push(`${m}: ${e.message}`); console.error(e); }
  }
  window.addEventListener("hashchange", route);
  // a phone turned between portrait and landscape crosses the narrow-screen tick rule: redraw the view
  let narrow = window.innerWidth < 420;
  window.addEventListener("resize", () => { const n = window.innerWidth < 420; if (n !== narrow) { narrow = n; route(); } });
  route();
  if (failed.length) box.insertAdjacentHTML("afterbegin", `<div class="err">Some features failed to load and are left out: ${failed.map(f => f.replace(/[<>&]/g, "")).join("; ")}</div>`);
}

start();
