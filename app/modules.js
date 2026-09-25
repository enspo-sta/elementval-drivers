/* modules.js: the features the viewer loads, one file each. To add a feature, put a new file in
 * app/views (a tab) or app/exporters (an export format) and add one line here. See EXTENDING.md. */
export default [
  "./views/drivers.js",
  "./views/compare.js",
  "./views/simulate.js",
  "./exporters/csv.js",
  "./exporters/rew.js",
  "./exporters/frd.js",
  "./exporters/zma.js",
  "./exporters/json.js",
];
