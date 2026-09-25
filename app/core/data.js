/* data.js: loads the database and its settings, and answers questions about them.
 * No page code here, so the tests and tools/export.mjs can use it in Node.js too. */

export const FILES = {
  main: "./drivers.json",
  survey: "./drivers_survey_midbass.json",
  sources: "./watch/config.json",
  kinds: "./schema/kinds.json",
  prices: "./prices.json",
};

export const store = { db: null, survey: null, families: [], kinds: [], kindById: {}, prices: null };

/** Load every file (the survey and the settings are optional). fetchJson(url) returns parsed JSON or null. */
export async function loadAll(fetchJson) {
  const [db, survey, config, kinds, prices] = await Promise.all([
    fetchJson(FILES.main), fetchJson(FILES.survey).catch(() => null),
    fetchJson(FILES.sources).catch(() => null), fetchJson(FILES.kinds).catch(() => null),
    fetchJson(FILES.prices).catch(() => null),
  ]);
  if (!db) throw new Error("drivers.json could not be read");
  setData({ db, survey, config, kinds, prices });
}

/** Use already-parsed files (tests, tools). */
export function setData({ db, survey, config, kinds, prices }) {
  store.db = db;
  store.prices = prices && prices.drivers ? prices : null;
  store.survey = survey || null;
  store.families = ((config && config.families) || []).slice().sort((a, b) => (a.rank || 99) - (b.rank || 99));
  store.kinds = (kinds && kinds.kinds) || [];
  store.kindById = Object.fromEntries(store.kinds.map(k => [k.id, k]));
  familyCache.clear();
}

export const num = v => {
  if (typeof v === "number") return v;
  const m = String(v == null ? "" : v).match(/^\s*(-?\d+(?:\.\d+)?)/);
  return m ? Number(m[1]) : null;
};

/** Every driver record: main database, the survey, or both. Comparison charts are not drivers. */
export function allDrivers({ survey = true } = {}) {
  const a = (store.db && store.db.drivers) || [];
  return survey && store.survey ? a.concat(store.survey.drivers) : a.slice();
}
export const driverById = id => allDrivers().find(d => d.id === id) || null;
export const isSurvey = d => !!(store.survey && store.survey.drivers.includes(d));

const familyCache = new Map();
/** The source family a measurement set comes from (watch/config.json), or null. */
export function familyOf(set) {
  const key = set.source || "";
  if (familyCache.has(key)) return familyCache.get(key);
  let found = null;
  for (const f of store.families) {
    try { if (new RegExp(f.match, "i").test(key)) { found = f; break; } } catch (e) { /* bad pattern in the settings */ }
  }
  familyCache.set(key, found);
  return found;
}

/** The kind of a measurement set (schema/kinds.json). Sets without a kind get a plain stand-in. */
export function kindOf(set) {
  const k = store.kindById[set.kind];
  if (k) return k;
  return { id: set.kind || "unknown", label: set.type || "Measurement", view: set.chartType === "bar" ? "bars" : set.chartType === "table" ? "table" : "curve",
           x: (set.axes && set.axes.x) || {}, y: (set.axes && set.axes.y) || {}, match: ["type"], export: ["csv", "json"] };
}

/** The sound pressure level a set was taken at (dB SPL at 1 m), or null. */
export function levelOf(set) {
  const c = set.conditions || {};
  const v = typeof c.spl_db === "number" ? c.spl_db : typeof c.ref_spl_db === "number" ? c.ref_spl_db : null;
  return v;
}

/** Two test tones of an intermodulation set as [f1, f2] Hz, or null. */
export function tonesOf(set) {
  const m = [set.method, set.type].join(" ").match(/(\d+(?:\.\d+)?)\s*\+\s*(\d+(?:\.\d+)?)\s*Hz/i);
  if (m) return [Number(m[1]), Number(m[2])];
  const c = set.conditions || {};
  const f1 = num(c.f1), f2 = num(c.f2);
  return f1 != null && f2 != null ? [f1, f2] : null;
}

/** Offers for a driver from prices.json, lowest first, or []. */
export function pricesOf(id) {
  const p = store.prices && store.prices.drivers[id];
  return p ? p.offers : [];
}
export const priceDate = () => (store.prices && store.prices.meta && store.prices.meta.updated) || null;
export const fmtSek = v => (v == null ? "" : Math.round(v).toLocaleString("sv-SE") + " kr");
export const fmtPrice = o => `${o.price.toLocaleString("sv-SE", { maximumFractionDigits: 2 })} ${o.currency}`;

export const fmtHz = f => (f >= 1000 ? Math.round(f / 100) / 10 + " kHz" : Math.round(f) + " Hz");
export const fmtLevel = L => (L == null ? "" : (Math.round(L * 10) / 10) + " dB");
