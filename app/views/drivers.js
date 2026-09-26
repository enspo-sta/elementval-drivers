/* drivers.js: the Drivers tab. The list of drivers, and each driver's page with every curve,
 * one source at a time or all sources. Curves of the same kind measured at several levels (for
 * example HiFiCompass's axial sound pressure and harmonics at several drive levels) share one chart,
 * one colour per level. */
import { registerView } from "../core/registry.js";
import { store, allDrivers, familyOf, kindOf, levelOf, isSurvey, pricesOf, priceDate, fmtSek, fmtPrice } from "../core/data.js";
import { quantitiesOf, matchKey, matchLabel, sortQuantities } from "../core/compare.js";
import { curvesOfSet, curvesOfDriver } from "../core/curves.js";
import { readHash, writeHash } from "../core/state.js";
import { $, app, esc, navHtml, beginView, newChart, noChart, noChartMsg, xAxis, yAxis, categoryAxis, chartOptions,
         barBase, barTop, levelColors, badge, condChips, exportHtml, wireExports, fmtHz } from "../core/ui.js";

const BRAND = "driver database";     // shown above the list; change to rebrand
const PALETTE = ["#f0a44a", "#6fd19a", "#7aa2f7", "#e98b8b", "#c4a3ff", "#f6c48a"];
const CONF = { high: "#6fd19a", medium: "#f0a44a", low: "#e98b8b", none: "#7b859c" };
const TS = [["Fs", "Hz"], ["Qts", ""], ["Vas", "L"], ["Sd", "cm²"], ["Xmax", "mm"], ["Bl", "T·m"], ["Re", "Ω"], ["Le", "mH"]];
const TS_EXTRA = { Vd: "cm³", Pe: "W", sens: "dB", sens1W: "dB/W", Mms: "g", Cms: "mm/N", Qms: "", Qes: "", Z: "Ω" };
const ROLE_ORDER = ["tweeter", "tweeter (waveguide)", "midrange", "midbass", "midbass / mid", "midbass (survey)",
                    "woofer / midbass", "woofer", "woofer (pair)", "comparison"];
const list = { filter: "", survey: false, scroll: 0, restore: false };
const cardState = {};                  // per chart card: the harmonic shown and the level shown, remembered while the page is open
// one colour per harmonic order when a single level is shown (the same colours as Simulate)
const ORDER_COLORS = { H2: "#f0a44a", H3: "#7aa2f7", H4: "#6fd19a", H5: "#c4a3ff", THD: "#eef0f6" };
const orderColor = (id, i) => ORDER_COLORS[id] || PALETTE[i % PALETTE.length];

// Comparison charts stored in drivers.json 'comparisons' are shown as extra records.
function comparisonRecords() {
  return ((store.db && store.db.comparisons) || []).map(c => ({ id: c.id, name: c.title, manufacturer: "", role: "comparison", band: "",
    isComparison: true, comparesN: (c.drivers || []).length, ts: {}, findings: "", measurements: [c] }));
}
function records() {
  return allDrivers({ survey: list.survey }).concat(comparisonRecords());
}
const roleRank = r => { const i = ROLE_ORDER.indexOf(r); return i < 0 ? 99 : i; };
function sourceNames(d) {
  const out = [];
  (d.measurements || []).forEach(m => { const f = familyOf(m); if (f && f.kind !== "derived" && !out.includes(f.name)) out.push(f.name); });
  return out;
}

function matches(d, q) {
  const text = [d.id, d.name, d.manufacturer, d.role, d.band, d.findings || "", d.isComparison ? "" : sourceNames(d).join(" ")].join(" ").toLowerCase();
  // "rs180" finds "RS 180-4": spaces and dashes do not count in model numbers
  const tight = s => s.replace(/[\s-]/g, "");
  return text.includes(q) || (q.length > 2 && tight(text).includes(tight(q)));
}

function showList() {
  beginView(false);
  shown.id = null;
  const surveyN = store.survey ? store.survey.drivers.length : 0;
  app().innerHTML = navHtml("drivers") + `<div class="kick"><span>${BRAND}</span><span style="color:var(--dim)" id="shown"></span></div>
    <h1>Driver database</h1>
    <input class="filter" id="flt" placeholder="filter by name, model, role, source, finding…" value="${esc(list.filter)}" autocomplete="off">
    <label class="ds"><input type="checkbox" id="surv" ${list.survey ? "checked" : ""}>
      include midbass intermodulation survey${surveyN ? ` (${surveyN} drivers · indicative)` : " (unavailable)"}</label>
    <div id="list"></div>`;
  fillList();
  // only the list below is redrawn while typing, so the caret and focus stay where they are
  $("flt").addEventListener("input", e => { list.filter = e.target.value; fillList(); });
  $("surv").addEventListener("change", e => { list.survey = e.target.checked; fillList(); });
  if (list.restore) { window.scrollTo(0, list.scroll); list.restore = false; }
}

function fillList() {
  const q = list.filter.trim().toLowerCase();
  const items = records().filter(d => matches(d, q))
    .sort((a, b) => roleRank(a.role) - roleRank(b.role) || (a.name || "").localeCompare(b.name || ""));
  $("shown").textContent = `${items.length} shown`;
  const box = $("list");
  box.innerHTML = "";
  if (!items.length) {
    box.innerHTML = `<div class="empty">No driver matches “${esc(list.filter.trim())}”${list.survey ? "" : " (the survey drivers are not included; tick the box above to search them too)"}.<br><button class="tog" id="clearflt">Clear the filter</button></div>`;
    $("clearflt").onclick = () => { list.filter = ""; $("flt").value = ""; fillList(); $("flt").focus(); };
    return;
  }
  let lastRole = null;
  for (const d of items) {
    if (d.role !== lastRole) { const hd = document.createElement("div"); hd.className = "rolehdr"; hd.textContent = d.role || "—"; box.appendChild(hd); lastRole = d.role; }
    const n = (d.measurements || []).length;
    const b = document.createElement("button");
    b.className = "card";
    const sub = d.isComparison ? `compares ${d.comparesN} drivers · ${(d.measurements[0].series || []).length} series`
      : `${[d.manufacturer, d.band].filter(Boolean).join(" · ") || "—"} · ${n} measurement${n !== 1 ? "s" : ""}`;
    const srcs = d.isComparison ? [] : sourceNames(d);
    const derivedOnly = !d.isComparison && !srcs.length && (d.measurements || []).some(m => (familyOf(m) || {}).kind === "derived");
    const offer = d.isComparison ? null : pricesOf(d.id).find(o => !o.pack) || null;
    b.innerHTML = `<div class="nm">${esc(d.name || "(unnamed)")}</div><div class="sub">${esc(sub)}</div>` +
      (srcs.length ? `<div class="srcs">${srcs.length > 1 ? srcs.length + " sources: " : "source: "}${esc(srcs.join(" · "))}</div>` : derivedOnly ? `<div class="srcs">calculated only (no measurement)</div>` : "") +
      (offer ? `<div class="from">from ${esc(offer.price_sek != null ? fmtSek(offer.price_sek) : fmtPrice(offer))} · ${esc(offer.shop)}</div>` : "");
    b.onclick = () => { list.scroll = window.scrollY; list.restore = true; location.hash = "driver/" + encodeURIComponent(d.id); };
    box.appendChild(b);
  }
}


// Sets of one driver grouped into chart cards: same source, kind and test conditions; levels together.
function cardsOf(d, sourceName) {
  const cards = [];
  (d.measurements || []).forEach((set, index) => {
    const fam = familyOf(set);
    if (sourceName && (!fam || fam.name !== sourceName)) return;
    const kind = kindOf(set);
    // an earlier capture that a full reading of the same charts superseded gets a card of its own, after the others
    const old = set.superseded_by ? "old" : "";
    const key = `${fam ? fam.name : "?"}::${kind.id}|${matchKey(set, kind)}|${kind.level ? "" : index}|${old}`;
    let c = cards.find(x => x.key === key);
    if (!c) { c = { key, fam, kind, sets: [], old: !!old }; cards.push(c); }
    c.sets.push({ set, index, level: levelOf(set), quantities: quantitiesOf(set, kind) });
  });
  const order = store.families.map(f => f.name);
  cards.forEach(c => c.sets.sort((a, b) => (a.level ?? 0) - (b.level ?? 0)));
  return cards.sort((a, b) => order.indexOf(a.fam && a.fam.name) - order.indexOf(b.fam && b.fam.name) || (a.old ? 1 : 0) - (b.old ? 1 : 0));
}

const levelName = s => (s.level != null ? `${Math.round(s.level * 10) / 10} dB` :
  (s.set.conditions || {}).drive_v != null ? `${[].concat(s.set.conditions.drive_v).join(" and ")} V` : s.set.method || `set ${s.index + 1}`);
// the name of a level in a card: its sound pressure, the drive voltage it came from, and what tells two sets
// at the same level apart (for example a chart without smoothing)
function levelNames(card) {
  const base = card.sets.map(s => {
    const v = (s.set.conditions || {}).drive_v;
    return levelName(s) + (s.level != null && v != null ? ` · ${[].concat(v).join(" and ")} V` : "");
  });
  return base.map((b, i) => {
    if (base.indexOf(b) === base.lastIndexOf(b)) return b;
    const m = String(card.sets[i].set.type || "").match(/\(([^)]*)\)\s*$/);
    return `${b} · ${m ? m[1] : "set " + (card.sets[i].index + 1)}`;
  });
}

// a note's web addresses become links (the chart a set was read from, a datasheet); the rest stays plain text
function linkify(text) {
  return esc(text).replace(/https?:\/\/[^\s<>"]+/g, u => {
    const tail = (u.match(/[.,;:)]+$/) || [""])[0], url = u.slice(0, u.length - tail.length);
    return `<a href="${url}" target="_blank" rel="noopener">${url}</a>${tail}`;
  });
}

// the driver page keeps its scroll position when a toggle or source button redraws the same driver
const shown = { id: null };

function showDetail(id, params) {
  const d = records().find(x => x.id === id) || (store.survey && store.survey.drivers.find(x => x.id === id));
  if (!d) {
    beginView(false);
    app().innerHTML = navHtml("drivers") + `<button class="back" id="bk">\u2190 all drivers</button><div class="empty">No driver with the id \u201c${esc(id)}\u201d in the database.</div>`;
    $("bk").onclick = () => { location.hash = ""; };
    return;
  }
  beginView(false);
  const keep = shown.id === d.id ? window.scrollY : 0;   // same driver redrawn: stay where the reader is
  const fams = [...new Set((d.measurements || []).map(m => familyOf(m)).filter(Boolean))]
    .sort((a, b) => (a.rank || 99) - (b.rank || 99));
  let src = params.get("src");
  if (src && !fams.some(f => f.name === src)) src = null;
  writeHash("driver/" + encodeURIComponent(d.id), { src });
  const extra = Object.entries(TS_EXTRA).filter(([k]) => d.ts && d.ts[k] != null && d.ts[k] !== "")
    .map(([k, u]) => `<b>${k}</b> ${esc(d.ts[k])}${u ? " " + u : ""}`).join("  ·  ");
  let h = navHtml("drivers") + `<button class="back" id="bk">← all drivers</button>${d.isComparison ? "" : `<button class="cmpbtn" id="cmpd">compare with other drivers</button>`}
    <h2>${esc(d.name)}</h2><div class="meta">${esc(d.isComparison ? "comparison · " + (d.comparesN || 0) + " drivers" : [d.manufacturer, d.role, d.band].filter(Boolean).join(" · "))}</div>`;
  const hasTs = !!d.ts && Object.values(d.ts).some(v => v != null && v !== "");
  if (!d.isComparison && !hasTs) h += `<div class="tsmore">No parameters stored yet.</div>`;
  if (!d.isComparison && hasTs) {
    h += `<div class="tsgrid">${TS.map(([k, u]) => `<div class="ts"><div class="k">${k}</div><div class="v">${d.ts && d.ts[k] != null && d.ts[k] !== "" ? esc(d.ts[k]) + (u ? `<span style="color:#7b859c;font-size:11px"> ${u}</span>` : "") : "—"}</div></div>`).join("")}</div>
      ${extra ? `<div class="tsmore">${extra}</div>` : ""}`;
  }
  if (!d.isComparison) h += pricesHtml(d) + completenessHtml(d);
  if (d.isComparison) {
    const cf = familyOf(d.measurements[0]);
    if (cf) h += `<div class="srcrow small"><span class="srcbtn on"><span class="sn">${esc(cf.name)}</span>${badge(cf)}</span></div>`;
  }
  if (fams.length && !d.isComparison) {
    h += `<div class="srcrow small">${[{ name: null }].concat(fams).map(f => {
      const n = (d.measurements || []).filter(m => !f.name || (familyOf(m) || {}).name === f.name).length;
      return `<button class="srcbtn${(src || null) === f.name ? " on" : ""}" data-src="${esc(f.name || "")}"><span class="sn">${esc(f.name || "All sources")}</span>${f.name ? badge(f) : ""}<span class="cnt">${n} set${n !== 1 ? "s" : ""}</span></button>`;
    }).join("")}</div>`;
    h += `<div class="exportrow">${exportHtml(() => curvesOfDriver(d, src), `${d.id}_${src || "all-sources"}`, "Export all curves")}</div>`;
  }
  const cards = d.isComparison ? [{ key: "cmp", fam: null, kind: kindOf(d.measurements[0]), sets: [{ set: d.measurements[0], index: 0, level: null, quantities: quantitiesOf(d.measurements[0]) }] }] : cardsOf(d, src);
  let lastFam;
  const draws = [];
  cards.forEach((c, ci) => {
    const famName = c.fam ? c.fam.name : "Other";
    if (!d.isComparison && famName !== lastFam) {
      const n = cards.filter(x => (x.fam ? x.fam.name : "Other") === famName).reduce((k, x) => k + x.sets.length, 0);
      h += `<div class="srchdr"><span>${esc(famName)}${c.fam && c.fam.reliability ? ` <b class="relt">· ${esc(c.fam.reliability)}</b>` : ""}</span><span>${n} set${n !== 1 ? "s" : ""}</span></div>`;
      lastFam = famName;
    }
    const first = c.sets[0].set;
    const multi = c.sets.length > 1;
    const conf = CONF[first.confidence] || CONF.none;
    const title = (multi ? `${c.kind.label}${matchLabel(first, c.kind) ? " · " + matchLabel(first, c.kind) : ""} · ${c.sets.length} levels`
      : `${first.type}${first.method ? " · " + first.method : ""}`) + (c.old ? " · earlier capture" : "");
    h += `<div class="setttl"><span>${esc(title)}</span><span class="conf" style="color:${conf};border:1px solid ${conf}55">${esc(first.confidence || "none")}</span></div>`;
    if (c.old) h += `<div class="setnote">Superseded: ${esc(first.superseded_by)}. Kept here as it was captured; Compare and Simulate use the newer sets.</div>`;
    const has = c.sets.some(s => s.quantities.length);
    if (!has) { h += `<div class="empty">no data</div>`; return; }
    let shownSets = c.sets;               // the sets whose conditions and notes are listed under the card
    if (multi && c.kind.view === "curve") {
      // two ways to look at several levels: one order at every level (all levels), or every order at one level
      const st = cardState[d.id + c.key] || {};
      const names = levelNames(c);
      const one = st.lv != null ? c.sets.find(s => String(s.index) === st.lv) || null : null;
      const ids = sortQuantities([...new Set((one ? [one] : c.sets).flatMap(s => s.quantities.map(q => q.id)))]);
      const all = !!one && ids.length > 1;          // "all orders" exists only for a single level
      const pick = st.q === "all" && all ? "all" : ids.includes(st.q) ? st.q : all ? "all" : ids[0];
      h += `<div class="togrow lvrow"><span class="rowlbl">Level</span><button class="tog small${one ? "" : " on"}" data-card="${ci}" data-lv="all">all levels</button>${c.sets.map((s, i) =>
        `<button class="tog small${one === s ? " on" : ""}" data-card="${ci}" data-lv="${s.index}">${esc(names[i])}</button>`).join("")}</div>`;
      if (ids.length > 1 || !one) h += `<div class="togrow"><span class="rowlbl">${one ? "Show" : "Order"}</span>${all ? `<button class="tog small${pick === "all" ? " on" : ""}" data-card="${ci}" data-q="all">all orders</button>` : ""}${ids.map(q =>
        `<button class="tog small${q === pick ? " on" : ""}" data-card="${ci}" data-q="${esc(q)}">${one ? `<span class="odot" style="background:${orderColor(q, ids.indexOf(q))}"></span>` : ""}${esc(q)}</button>`).join("")}</div>`;
      if (one) {
        shownSets = [one];
        const qs = pick === "all" ? ids : [pick];
        h += `<div class="legend">${qs.map(q => `<span class="lg"><span class="lgl" style="background:${orderColor(q, ids.indexOf(q))}"></span>${esc(q)} at ${esc(names[c.sets.indexOf(one)])}</span>`).join("")}</div>`;
        h += noChart() ? noChartMsg : `<div class="chartbox"><canvas id="ch${ci}"></canvas></div>`;
        draws.push(() => drawOneLevel($("ch" + ci), c, one, qs, ids, names[c.sets.indexOf(one)]));
        h += overlayHtml(d, one.set, one.index, qs);
      } else {
        const cols = levelColors(c.sets.length);
        h += `<div class="legend">${c.sets.map((s, i) => `<span class="lg"><span class="lgl" style="background:${cols[i]}"></span>${esc(names[i])}</span>`).join("")}</div>`;
        h += noChart() ? noChartMsg : `<div class="chartbox"><canvas id="ch${ci}"></canvas></div>`;
        draws.push(() => drawLevels($("ch" + ci), c, pick, cols, names));
        if (c.sets.some(x => x.set.calibration)) h += `<div class="hint2">Pick one level above to check its reading against the source chart.</div>`;
      }
    } else if (multi && c.kind.view === "bars") {
      const cols = levelColors(c.sets.length);
      h += `<div class="legend">${c.sets.map((s, i) => `<span class="lg"><span class="lgl sq" style="background:${cols[i]}"></span>${esc(levelName(s))}</span>`).join("")}</div>`;
      h += noChart() ? noChartMsg : `<div class="chartbox"><canvas id="ch${ci}"></canvas></div>`;
      draws.push(() => drawLevelBars($("ch" + ci), c, cols));
    } else {
      for (const s of c.sets) {
        if (s.set.chartType === "table") { h += renderTable(s.set); continue; }
        const series = s.set.series || [];
        const ylab = (((s.set.axes || {}).y || {}).label || "").toLowerCase();
        if (c.kind.view === "bars" && /^spl$/.test(ylab)) h += `<div class="setnote">Shown as published: the sound pressure of every bar, test tones included. Compare and the export give the products relative to the upper tone, without the tones.</div>`;
        if (series.length > 1) h += `<div class="legend">${series.map((x, i) => `<span class="lg"><span class="lgl" style="background:${PALETTE[i % PALETTE.length]}"></span>${esc(x.name)}</span>`).join("")}</div>`;
        h += noChart() ? noChartMsg : `<div class="chartbox"><canvas id="ch${ci}_${s.index}"></canvas></div>`;
        draws.push(() => drawSet($("ch" + ci + "_" + s.index), s.set));
        h += overlayHtml(d, s.set, s.index, null);
      }
    }
    const notes = new Set();
    for (const s of shownSets) {
      h += condChips(s.set.conditions, s.set.source);
      // the same note on several levels of one measurement is shown once
      if (s.set.note && !notes.has(s.set.note)) { notes.add(s.set.note); h += `<div class="setnote">${linkify(s.set.note)}</div>`; }
    }
    h += `<div class="exportrow">${exportHtml(() => c.sets.flatMap(s => curvesOfSet(d, s.set)), `${d.id}_${c.kind.id}${c.fam ? "_" + c.fam.name : ""}`)}</div>`;
  });
  if (!cards.length) h += `<div class="empty">No measurements from this source.</div>`;
  if (d.findings) h += `<div class="findings">${esc(d.findings)}</div>`;
  app().innerHTML = h;
  $("bk").onclick = () => { location.hash = ""; };
  const cb = $("cmpd");
  if (cb) cb.onclick = () => { location.hash = "compare?driver=" + encodeURIComponent(d.id); };
  document.querySelectorAll("[data-src]").forEach(b => b.onclick = () => {
    const p = new URLSearchParams(); if (b.dataset.src) p.set("src", b.dataset.src);
    showDetail(d.id, p);
  });
  document.querySelectorAll("[data-card]").forEach(b => b.onclick = () => {
    const key = d.id + cards[Number(b.dataset.card)].key, st = cardState[key] || (cardState[key] = {});
    if (b.dataset.q != null) st.q = b.dataset.q;
    if (b.dataset.lv != null) {
      st.lv = b.dataset.lv === "all" ? null : b.dataset.lv;
      // one level: every order at once; back to all levels: one order (the one shown before, else the first)
      if (st.lv != null) { st.back = st.q !== "all" ? st.q : st.back; st.q = "all"; } else if (st.q === "all") st.q = st.back;
    }
    showDetail(d.id, readHash().params);
  });
  draws.forEach(f => f());
  document.querySelectorAll("[data-ovl]").forEach(b => b.onclick = () => {
    cardState[b.dataset.ovl] = !cardState[b.dataset.ovl];
    showDetail(d.id, readHash().params);
  });
  document.querySelectorAll(".ovlbox img").forEach(img => {
    const box = img.parentElement, set = d.measurements[Number(box.dataset.set)], only = box.dataset.q ? box.dataset.q.split(",") : null;
    const draw = () => drawOverlay(box.querySelector("canvas"), img, set, only);
    img.onload = draw;
    img.onerror = () => { box.classList.add("failed"); box.nextElementSibling.insertAdjacentHTML("afterbegin", `<b>The chart image could not be loaded here</b> (this page may not be allowed to show images from other sites, or you are offline). `); };
    if (img.complete && img.naturalWidth) draw();
  });
  wireExports(app());
  window.scrollTo(0, keep);
  shown.id = d.id;
}

// Does this driver have every curve its source publishes? From watch/completeness.json (capture/completeness.py).
function completenessHtml(d) {
  const r = store.completeness && store.completeness.drivers[d.id];
  if (!r) return "";
  const s = r.summary || {};
  const head = r.page
    ? `${s.published} chart${s.published !== 1 ? "s" : ""} on its HiFiCompass page · ${s.stored} stored` + (s.by_hand ? ` · ${s.by_hand} by hand` : "") + ` · ${s.missing} not stored`
    : r.page_note || "no HiFiCompass measurement page for this exact variant";
  const dsMiss = (r.datasheet_kinds || []).filter(x => !x.stored);
  let body = "";
  if (r.page) {
    const kinds = {};
    r.charts.forEach(c => { const k = kinds[c.label] || (kinds[c.label] = { stored: 0, hand: 0, missing: 0, why: new Set() }); if (c.state === "stored") k.stored++; else if (c.state === "by hand") k.hand++; else { k.missing++; k.why.add(c.why); } });
    body += `<p class="dim">Page: <a href="${esc(r.page)}" target="_blank" rel="noopener">${esc(r.page)}</a>${r.data_files && r.data_files.length ? ` · files offered: ${r.data_files.map(u => `<a href="${esc(u)}" target="_blank" rel="noopener">${esc(u.split("/").pop())}</a>`).join(", ")}` : ""}</p>`;
    body += `<div class="tscroll"><table class="dtable ctab cmpl"><thead><tr><th>Chart</th><th>On the page</th><th>Stored</th><th>Not stored, why</th></tr></thead><tbody>${Object.entries(kinds).map(([label, k]) =>
      `<tr><td>${esc(label)}</td><td>${k.stored + k.hand + k.missing}</td><td>${k.stored}${k.hand ? ` + ${k.hand} by hand` : ""}</td><td>${k.missing ? `${k.missing}: ${esc([...k.why].join("; "))}` : "—"}</td></tr>`).join("")}</tbody></table></div>`;
    const miss = r.charts.filter(c => c.state === "missing");
    if (miss.length) body += `<details class="conds"><summary>The ${miss.length} chart${miss.length !== 1 ? "s" : ""} not stored</summary><ul class="how">${miss.map(c =>
      `<li><a href="${esc(c.url)}" target="_blank" rel="noopener">${esc(c.file)}</a> · ${esc(c.label)}${c.volts != null ? " · " + esc(c.volts) + " V" : ""}</li>`).join("")}</ul></details>`;
  }
  if (r.datasheet_kinds) body += `<p class="dim">Purifi datasheet figures: ${r.datasheet_kinds.map(x => `${esc(x.what)} ${x.stored ? "stored" : "<b>not stored</b>"}`).join(" · ")}</p>`;
  const done = r.page ? s.missing === 0 && !dsMiss.length : !dsMiss.length;
  return `<details class="cmplbox"><summary><span class="lbl2">Every curve from the source?</span> <span class="${done ? "ok" : "dim"}">${esc(head)}${dsMiss.length ? ` · ${dsMiss.length} datasheet figure${dsMiss.length !== 1 ? "s" : ""} not stored` : ""}</span></summary>${body}
    <p class="dim">Checked ${esc(store.completeness.date)} against the HiFiCompass inventory of ${esc(store.completeness.inventory_date || "?")} (capture/completeness.py).</p></details>`;
}

// Lowest prices from prices.json (rebuilt weekly by watch/prices.py).
function pricesHtml(d) {
  const offers = pricesOf(d.id), date = priceDate();
  if (!store.prices) return "";
  if (!offers.length) return `<div class="price"><div class="lbl"><span>Price in Europe</span><span class="hint">${date ? "checked " + esc(date) : "not checked yet"}</span></div><span class="dim">${date ? "No price found at the shops checked. " : "The weekly price scan has not run yet. "}Shops: ${esc(((store.prices.meta || {}).shops_scanned || []).join(", ") || "see watch/prices_config.json")}.</span></div>`;
  // a logged-in price recorded by hand (capture/CHROME_CAPTURE.md) counts before the public price
  const eff = o => (o.price_logged_in != null ? o.price_logged_in : o.price);
  const sek = o => (o.price_sek != null && o.price ? Math.round(o.price_sek * eff(o) / o.price) : null);
  // lowest in kronor first; an offer whose currency could not be converted goes last
  const sorted = offers.slice().sort((a, b) => (sek(a) ?? Infinity) - (sek(b) ?? Infinity));
  const best = sorted.find(o => !o.pack && !o.doubtful) || sorted.find(o => !o.pack) || sorted[0];   // a box price or a doubtful one is never the headline
  // what the scan says about an offer: the shop's note, a price kept from an earlier scan, a doubtful reading
  const noteOf = o => [o.shop_note, o.kept_from ? "price from the scan of " + o.kept_from + " (the shop could not be reached at the last scan)" : "", o.doubtful ? "doubtful: far from the other shops" : "", o.price_note && !o.kept_from && !o.doubtful ? o.price_note : ""].filter(Boolean).join(" · ");
  const priceText = o => `${eff(o).toLocaleString("sv-SE", { maximumFractionDigits: 2 })} ${o.currency}` + (o.pack ? " (price for a box, not one driver)" : "") + (o.price_logged_in != null ? " (logged in)" : o.login_prices ? " (public price; lower when logged in)" : "");
  return `<div class="price"><div class="lbl"><span>${best.pack ? "Price in Europe (a box only)" : "Lowest price in Europe"}</span><span class="hint">checked ${esc(date)} · prices and stock change: check the shop</span></div>
    <div class="from">${esc(sek(best) != null ? fmtSek(sek(best)) : priceText(best))} <small>${sek(best) != null ? esc(priceText(best)) + " at " : "at "}<a href="${esc(best.url)}" target="_blank" rel="noopener">${esc(best.shop)}</a> (${esc(best.country)})${best.availability ? " · " + esc(best.availability) : ""}${noteOf(best) ? " · " + esc(noteOf(best)) : ""}</small></div>
    ${sorted.length > 1 ? `<div class="tscroll"><table class="dtable ctab"><thead><tr><th>Shop</th><th>Price</th><th>In kronor</th><th>Stock</th><th>Note</th></tr></thead><tbody>${sorted.map(o =>
      `<tr><td><a href="${esc(o.url)}" target="_blank" rel="noopener">${esc(o.shop)}</a> (${esc(o.country)})</td><td>${esc(priceText(o))}</td><td>${esc(sek(o) != null ? fmtSek(sek(o)) : "—")}</td><td>${esc(o.availability || "—")}</td><td>${esc(noteOf(o))}</td></tr>`).join("")}</tbody></table></div>` : ""}</div>`;
}

function renderTable(set) {
  const cols = set.columns || [], rows = set.rows || [];
  // values as stored (0.054 stays 0.054); only very long decimals are shortened
  const fmt = v => (v === null || v === undefined || v === "" ? "—" : typeof v === "number" ? (Number.isInteger(v) ? v : Math.abs(v) >= 1000 ? v.toFixed(1) : +v.toPrecision(4)) : esc(v));
  return `<div class="tscroll"><table class="dtable"><thead><tr>${cols.map(c => `<th>${esc(c)}</th>`).join("")}</tr></thead>` +
    `<tbody>${rows.map(r => `<tr>${r.map(c => `<td>${fmt(c)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
}

function drawSet(canvas, set) {
  if (!canvas) return;
  const ax = set.axes || { x: {}, y: {} };
  const xt = ((ax.x && ax.x.label) || "") + (ax.x && ax.x.unit ? " (" + ax.x.unit + ")" : "");
  // harmonics stored as sound pressure (a datasheet figure) are shown as ratios, as Compare and the export do
  const kind = kindOf(set), ylab = ((ax.y && ax.y.label) || "").toLowerCase();
  const off = kind && kind.ratio && /^spl$/.test(ylab) && levelOf(set) != null ? -levelOf(set) : 0;
  const yt = off ? `dB re fundamental (stored as SPL at ${levelOf(set)} dB)` : ((ax.y && ax.y.label) || "") + (ax.y && ax.y.unit ? " (" + ax.y.unit + ")" : "");
  const isBar = set.chartType === "bar";
  const ys = (set.series || []).flatMap(s => (s.points || []).map(p => p.y)).filter(v => v != null).map(v => Number(v) + off);
  const base = isBar ? barBase(ys) : undefined;
  const logX = !isBar && ax.x && ax.x.scale === "log";
  const ds = (set.series || []).map((s, i) => {
    const pts = (s.points || []).map(p => ({ x: Number(p.x), y: p.y == null ? null : Number(p.y) + off }));
    return { label: s.name, data: isBar ? pts : withBreaks(pts, logX), spanGaps: false,
      backgroundColor: isBar ? "#f0a44a" : PALETTE[i % PALETTE.length], borderColor: PALETTE[i % PALETTE.length],
      borderWidth: isBar ? 0 : 2, pointRadius: 0, tension: 0.25, barThickness: isBar ? 6 : undefined, base };
  });
  // bars grow up from the bottom (as in Compare), so a taller bar is always more distortion
  const opts = chartOptions({ x: xAxis(!isBar && ax.x && ax.x.scale === "log", xt), y: yAxis("db", yt, isBar ? { min: base, max: barTop(ys) } : {}) });
  newChart(canvas, { type: isBar ? "bar" : "line", data: { datasets: ds }, options: opts });
}

// Several levels of a bar measurement (an intermodulation spectrum at 70, 80, 85 dB): grouped bars, one colour per level.
function drawLevelBars(canvas, card, cols) {
  if (!canvas) return;
  // only frequencies where at least one level has a value (a stored null is not a bar)
  const freqs = [...new Set(card.sets.flatMap(s => ((s.set.series[0] || {}).points || []).filter(p => p.y != null).map(p => Number(p.x))))].sort((a, b) => a - b);
  const all = card.sets.flatMap(s => ((s.set.series[0] || {}).points || []).map(p => p.y)).filter(v => v != null);
  const base = barBase(all);
  const ds = card.sets.map((s, i) => ({ label: levelName(s), backgroundColor: cols[i], base,
    data: freqs.map(f => { const pt = ((s.set.series[0] || {}).points || []).find(p => Number(p.x) === f); return pt && pt.y != null ? Number(pt.y) : null; }) }));
  const yUnit = ((card.kind.y || {}).unit) || (((card.sets[0].set.axes || {}).y || {}).unit) || "";
  newChart(canvas, { type: "bar", data: { labels: freqs.map(fmtHz), datasets: ds },
    options: chartOptions({ x: categoryAxis("Product frequency", 50), y: yAxis("db", yUnit, { min: base, max: barTop(all) }) },
      c => `${c.dataset.label}: ${c.parsed.y.toFixed(1)} at ${c.label}`) });
}

// Points of a curve for a chart: where the source curve has a stretch without points wider than 1/6 octave and
// three times the curve's own spacing (the automatic reading could not see the curve there), the line breaks
// instead of bridging it. A sparse hand capture (a point every 2/3 octave) is drawn whole. Same rule as Simulate.
function withBreaks(points, log) {
  const pts = points.map(p => ({ x: Number(p.x), y: p.y })).filter(p => p.x > 0);
  if (!log || pts.length < 3) return pts;
  const steps = pts.slice(1).map((p, i) => Math.log2(p.x / pts[i].x)).filter(v => v > 0).sort((a, b) => a - b);
  const limit = Math.max(1 / 6, 3 * (steps[Math.floor(steps.length / 2)] || 0));
  const out = [];
  pts.forEach((p, i) => {
    const prev = pts[i - 1];
    if (prev && Math.log2(p.x / prev.x) > limit) out.push({ x: Math.sqrt(prev.x * p.x), y: null });
    out.push(p);
  });
  return out;
}

function drawLevels(canvas, card, quantity, cols, names) {
  if (!canvas) return;
  const log = (card.kind.x || {}).scale === "log";
  const ds = card.sets.map((s, i) => {
    const q = s.quantities.find(x => x.id === quantity);
    return { label: names ? names[i] : levelName(s), data: q ? withBreaks(q.points, log) : [], borderColor: cols[i], backgroundColor: cols[i],
             borderWidth: 2, pointRadius: 0, tension: 0.2, spanGaps: false };
  });
  const k = card.kind;
  newChart(canvas, { type: "line", data: { datasets: ds }, options: chartOptions({
    x: xAxis((k.x || {}).scale === "log", `${(k.x || {}).label || ""}${(k.x || {}).unit ? " (" + k.x.unit + ")" : ""}`),
    y: yAxis("db", `${quantity} (${(k.y || {}).unit || ""})`) },
    c => `${c.dataset.label}: ${c.parsed.y.toFixed(1)} at ${(k.x || {}).scale === "log" ? fmtHz(c.parsed.x) : c.parsed.x}`) });
}

// The check a person does by eye: the source's own chart image with our reading drawn on it (dashed magenta).
// The image is loaded from the source's site in the reader's browser; nothing is copied or stored.
function overlayHtml(d, set, index, qs) {
  const cal = set.calibration;
  if (!cal || !cal.image || noChart()) return "";
  const key = d.id + "|ovl|" + index, on = !!cardState[key];
  const share = set.check && set.check.on_curve ? Object.entries(set.check.on_curve).map(([k, v]) => `${k} ${Math.round(v * 100)} %`).join(", ") : "";
  return `<div class="ovlrow"><button class="tog small${on ? " on" : ""}" data-ovl="${esc(key)}">${on ? "hide the source chart" : "check against the source chart"}</button>${share ? `<span class="dim">read points on the drawn curve: ${esc(share)}</span>` : ""}</div>` +
    (on ? `<div class="ovlbox" data-set="${index}" data-q="${esc((qs || []).join(","))}" style="aspect-ratio:${cal.width}/${cal.height}"><img src="${esc(cal.image)}" alt="the source chart" referrerpolicy="no-referrer"><canvas></canvas></div>
      <div class="hint2">The source's own chart, with this reading drawn on it in dashed magenta: where the magenta sits on the original line, the reading is right. <a href="${esc(cal.image)}" target="_blank" rel="noopener">Open the chart</a>.</div>` : "");
}

function drawOverlay(canvas, img, set, only) {
  const cal = set.calibration;
  if (!canvas || !cal) return;
  const w = img.clientWidth, h = img.clientHeight, dpr = window.devicePixelRatio || 1;
  canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr);
  canvas.style.width = w + "px"; canvas.style.height = h + "px";
  const g = canvas.getContext("2d");
  g.setTransform(dpr * w / cal.width, 0, 0, dpr * h / cal.height, 0, 0);
  g.lineWidth = 2 * cal.width / w; g.setLineDash([6 * cal.width / w, 4 * cal.width / w]); g.strokeStyle = "#ff2bd6";
  for (const s of set.series || []) {
    if (only && only.length && !only.includes(s.name)) continue;
    g.beginPath();
    let open = false, prev = null;
    for (const p of s.points || []) {
      if (p.y == null || !(p.x > 0)) { open = false; continue; }
      const x = (Math.log10(p.x) - cal.x[0]) / cal.x[1], y = (p.y - cal.y[0]) / cal.y[1];
      // the same breaks as the chart: no line across a stretch the reading could not see
      if (open && prev && Math.log2(p.x / prev) > 1 / 6) open = false;
      if (open) g.lineTo(x, y); else g.moveTo(x, y);
      open = true; prev = p.x;
    }
    g.stroke();
  }
}

// One level of a card: the chosen orders of that one set, one colour per order.
function drawOneLevel(canvas, card, one, qs, ids, name) {
  if (!canvas) return;
  const k = card.kind, log = (k.x || {}).scale === "log";
  const ds = qs.map(id => {
    const q = one.quantities.find(x => x.id === id), col = orderColor(id, ids.indexOf(id));
    return { label: `${id} at ${name}`, data: q ? withBreaks(q.points, log) : [], borderColor: col, backgroundColor: col,
             borderWidth: id === "THD" ? 3 : 2, pointRadius: 0, tension: 0.2, spanGaps: false };
  });
  const unit = (k.y || {}).unit || "";
  newChart(canvas, { type: "line", data: { datasets: ds }, options: chartOptions({
    x: xAxis(log, `${(k.x || {}).label || ""}${(k.x || {}).unit ? " (" + k.x.unit + ")" : ""}`),
    y: yAxis("db", `${qs.length === 1 ? qs[0] : (k.y || {}).label || "Level"} (${unit})`) },
    c => `${c.dataset.label}: ${c.parsed.y.toFixed(1)} at ${log ? fmtHz(c.parsed.x) : c.parsed.x}`) });
}

registerView({
  id: "drivers", label: "Drivers", order: 10, routes: ["", "driver"],
  show({ page, rest, params }) {
    if (page === "driver" && rest) {
      const d = records().find(x => x.id === rest) || (store.survey && store.survey.drivers.find(x => x.id === rest));
      if (d && isSurvey(d)) list.survey = true;
      return showDetail(rest, params);
    }
    return showList();
  },
});
