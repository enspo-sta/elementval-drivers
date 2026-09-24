/* registry.js: where features plug in. A feature is one file in app/views or app/exporters that
 * calls one of the register functions below; app/modules.js lists the files to load. Nothing else
 * has to change to add a tab or an export format. */

const views = [];
const exporters = [];

/**
 * A tab of the viewer.
 * { id, label, order (position in the tab bar), nav (show in the tab bar, default true),
 *   routes: ["compare"]   (the first part of the address after '#'; "" is the start page),
 *   show({ page, rest, params })   draws the view into #app; params are the settings in the address }
 */
export function registerView(view) {
  if (!view || !view.id || typeof view.show !== "function") throw new Error("registerView needs an id and a show() function");
  const i = views.findIndex(v => v.id === view.id);
  if (i >= 0) views.splice(i, 1);
  views.push(Object.assign({ nav: true, order: 50, routes: [view.id] }, view));
}

/**
 * An export format.
 * { id, label, ext, mime, order,
 *   accepts(curve) -> true when this format can hold the curve,
 *   files(curves, { title }) -> [{ name, text }]   (see app/exporters/README in EXTENDING.md) }
 */
export function registerExporter(exp) {
  if (!exp || !exp.id || typeof exp.files !== "function") throw new Error("registerExporter needs an id and a files() function");
  const i = exporters.findIndex(e => e.id === exp.id);
  if (i >= 0) exporters.splice(i, 1);
  exporters.push(Object.assign({ order: 50, accepts: () => true, mime: "text/plain" }, exp));
}

export const getViews = () => views.slice().sort((a, b) => a.order - b.order);
export const getExporters = () => exporters.slice().sort((a, b) => a.order - b.order);
export const viewForPage = page => views.find(v => v.routes.includes(page)) || views.find(v => v.routes.includes(""));
