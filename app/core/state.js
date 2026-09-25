/* state.js: settings kept in the address after '#', so a view can be bookmarked or sent as a link.
 * "#compare?src=HiFiCompass&q=H3" -> page "compare", params src and q. */

export function readHash() {
  const h = location.hash.slice(1);
  const q = h.indexOf("?");
  const path = q < 0 ? h : h.slice(0, q);
  const slash = path.indexOf("/");
  return { page: slash < 0 ? path : path.slice(0, slash), rest: slash < 0 ? "" : decodeURIComponent(path.slice(slash + 1)),
           params: new URLSearchParams(q < 0 ? "" : h.slice(q + 1)) };
}

/** Write the settings of the open view into the address without adding a history step. */
export function writeHash(page, obj) {
  const p = new URLSearchParams();
  for (const [k, v] of Object.entries(obj)) if (v != null && v !== "") p.set(k, v);
  const s = p.toString();
  try { history.replaceState(null, "", "#" + page + (s ? "?" + s : "")); } catch (e) { /* some embedded frames refuse; the view still works */ }
}

export const hasParams = params => [...params.keys()].length > 0;
