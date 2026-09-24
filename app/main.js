/* main.js: starts the viewer. Loads the data, loads every feature listed in modules.js, and shows
 * the view the address asks for ('#compare', '#driver/<id>', ...). */
import { loadAll } from "./core/data.js";
import { viewForPage } from "./core/registry.js";
import { readHash } from "./core/state.js";
import MODULES from "./modules.js";

const fetchJson = url => fetch(url, { cache: "no-cache" }).then(r => { if (!r.ok) throw new Error(`${url}: HTTP ${r.status}`); return r.json(); });

function route() {
  const where = readHash();
  const view = viewForPage(where.page);
  if (view) view.show(where);
}

async function start() {
  const box = document.getElementById("app");
  try {
    await loadAll(fetchJson);
  } catch (e) {
    box.innerHTML = `<div class="err">Couldn't load the database: ${e.message}. Make sure drivers.json sits next to index.html.</div>`;
    return;
  }
  const failed = [];
  for (const m of MODULES) {
    try { await import(m); } catch (e) { failed.push(`${m}: ${e.message}`); console.error(e); }
  }
  window.addEventListener("hashchange", route);
  route();
  if (failed.length) box.insertAdjacentHTML("afterbegin", `<div class="err">Some features failed to load and are left out: ${failed.map(f => f.replace(/[<>&]/g, "")).join("; ")}</div>`);
}

start();
