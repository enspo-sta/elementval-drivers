// Browser tests of the viewer: every tab, the exports, an empty search, and phone, tablet and laptop
// screen sizes. Run: npm run test:browser   (needs: npm install, then npx playwright install chromium)
// Skips itself when Playwright is not installed. Serves the repository on a free port itself.
import test from "node:test";
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { readFile, mkdtemp, readFile as readF, stat } from "node:fs/promises";
import { createRequire } from "node:module";
import { tmpdir } from "node:os";
import { join, extname } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = fileURLToPath(new URL("..", import.meta.url));
const TYPES = { ".html": "text/html", ".js": "text/javascript", ".mjs": "text/javascript", ".css": "text/css", ".json": "application/json", ".md": "text/markdown" };
let playwright = null;
try { playwright = createRequire(import.meta.url)("playwright"); }
catch (e) { try { playwright = createRequire(join(process.env.NODE_PATH || "/nonexistent", "x"))("playwright"); } catch (e2) { playwright = null; } }

const SIZES = {
  "narrow phone 320": [320, 568], "Android 360": [360, 800], "iPhone 375": [375, 667], "iPhone 390": [390, 844],
  "phone landscape 844": [844, 390], "iPad 768": [768, 1024], "iPad 820": [820, 1180], "iPad landscape 1180": [1180, 820],
  "13-inch laptop 1280": [1280, 800], "laptop 1440": [1440, 900],
};

let server, base, browser, dl;
test.before(async () => {
  if (!playwright) return;
  server = createServer(async (req, res) => {
    const path = decodeURIComponent(new URL(req.url, "http://x").pathname);
    const file = join(ROOT, path === "/" ? "index.html" : path);
    try {
      const body = await readFile(file);
      res.writeHead(200, { "Content-Type": TYPES[extname(file)] || "application/octet-stream" });
      res.end(body);
    } catch (e) { res.writeHead(404); res.end("not found"); }
  });
  await new Promise(r => server.listen(0, "127.0.0.1", r));
  base = `http://127.0.0.1:${server.address().port}/index.html`;
  browser = await playwright.chromium.launch();
  dl = await mkdtemp(join(tmpdir(), "viewer-dl-"));
});
test.after(async () => { if (browser) await browser.close(); if (server) server.close(); });

async function open(hash, size = SIZES["13-inch laptop 1280"]) {
  const ctx = await browser.newContext({ viewport: { width: size[0], height: size[1] }, acceptDownloads: true });
  const page = await ctx.newPage();
  const errors = [];
  page.on("pageerror", e => errors.push("pageerror " + e.message));
  page.on("console", m => { if (m.type() === "error") errors.push("console " + m.text()); });
  await page.route("**/fonts.googleapis.com/**", r => r.fulfill({ body: "", contentType: "text/css" }));
  await page.goto(base + hash);
  await page.waitForSelector(".tabs");
  return { page, ctx, errors, close: () => ctx.close() };
}
const noSidewaysScroll = page => page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth);
const chartCount = page => page.evaluate(() => Object.keys(Chart.instances).length);
const skip = () => !playwright;

test("Drivers list: loads, filters, and an empty search says so", { skip: skip() }, async () => {
  const { page, errors, close } = await open("");
  assert.ok((await page.$$(".card")).length >= 17);
  assert.deepEqual(await page.$$eval(".tabs a", a => a.map(x => x.textContent)), ["Drivers", "Compare", "Simulate"]);
  await page.fill("#flt", "ptt5.25");
  assert.equal((await page.$$(".card")).length, 1);
  await page.fill("#flt", "zzzz-nothing");
  assert.equal((await page.$$(".card")).length, 0);
  const empty = await page.textContent(".empty");
  assert.match(empty, /no driver/i);
  await page.click("#clearflt");
  assert.ok((await page.$$(".card")).length >= 17, "clearing the filter brings the list back");
  await page.check("#surv");
  assert.ok((await page.$$(".card")).length >= 36, "survey drivers added");
  assert.deepEqual(errors, []);
  await close();
});

test("Driver page: sources, level charts, export download", { skip: skip() }, async () => {
  const { page, errors, close } = await open("#driver/purifi-ptt8-0x04-nab-02");
  await page.waitForSelector("#bk");
  assert.ok((await page.$$("[data-src]")).length >= 3, "All sources + one button per source");
  await page.click('[data-src="HiFiCompass"]');
  assert.match(await page.evaluate(() => location.hash), /src=HiFiCompass/);
  assert.ok(await page.$("text=2 levels"), "the two HiFiCompass levels share one chart");
  assert.ok(await page.$("text=Lowest price in Europe"), "the price card from prices.json");
  assert.match(await page.textContent(".price"), /kr/, "the lowest price is given in kronor");
  assert.ok((await chartCount(page)) >= 1);
  const [download] = await Promise.all([page.waitForEvent("download"), page.click(".exportrow >> nth=0 >> [data-dl]")]);
  const file = join(dl, download.suggestedFilename());
  await download.saveAs(file);
  assert.ok((await stat(file)).size > 200, "the CSV is not empty");
  assert.match(await readF(file, "utf8"), /^Frequency \(Hz\),/m);
  assert.deepEqual(errors, []);
  await close();
});

test("An unknown driver id gets a message and a way back", { skip: skip() }, async () => {
  const { page, errors, close } = await open("#driver/does-not-exist");
  await page.waitForSelector("#bk");
  assert.match(await page.textContent(".empty"), /No driver with the id/);
  await page.click("#bk");
  await page.waitForSelector("#flt");
  assert.deepEqual(errors, []);
  await close();
});

test("Every driver page opens without errors", { skip: skip() }, async () => {
  const db = JSON.parse(await readFile(join(ROOT, "drivers.json"), "utf8"));
  const survey = JSON.parse(await readFile(join(ROOT, "drivers_survey_midbass.json"), "utf8"));
  const ids = db.drivers.map(d => d.id).concat(survey.drivers.map(d => d.id), db.comparisons.map(c => c.id));
  const { page, errors, close } = await open("");
  for (const id of ids) {
    await page.goto(base + "#driver/" + encodeURIComponent(id));
    await page.waitForSelector("#bk");
    assert.ok(await page.$("h2"), id);
  }
  assert.deepEqual(errors, []);
  await close();
});

test("Compare: five drivers, one quantity, level buttons, the limit, export", { skip: skip() }, async () => {
  const { page, errors, close } = await open("#compare");
  await page.waitForSelector("#cchart");
  await page.click('[data-src="HiFiCompass"]');
  await page.waitForSelector("#cchart");
  assert.ok((await page.$$(".pick.on")).length === 5, "five picked by default");
  assert.ok((await page.$$("[data-pick]:disabled")).length >= 1, "the sixth is disabled");
  await page.click('[data-q="H3"]'); await page.click('[data-q="H2"]');
  assert.deepEqual(await page.$$eval(".tog.on[data-q]", b => b.map(x => x.textContent.trim())), ["H3"]);
  assert.equal(await page.evaluate(() => Object.values(Chart.instances)[0].data.datasets.length), 5);
  await page.click('[data-lvl="91"]');
  assert.match(await page.textContent(".ptitle"), /target 91 dB/);
  await page.check("#cshift");
  assert.match(await page.textContent(".legend"), /moved to 91 dB/);
  const [download] = await Promise.all([page.waitForEvent("download"), page.click(".exportrow [data-dl]")]);
  assert.match(download.suggestedFilename(), /^comparison_/);
  for (let i = 0; i < 5; i++) { await page.click(".pick.on input"); await page.waitForTimeout(100); }
  assert.match(await page.evaluate(() => location.hash), /d=none/, "no driver picked is kept in the address");
  await page.reload(); await page.waitForSelector(".tabs"); await page.waitForTimeout(300);
  assert.equal((await page.$$(".pick.on")).length, 0, "still none picked after a reload");
  assert.match(await page.textContent(".panel:last-of-type, #app"), /Pick at least one driver/);
  for (let i = 0; i < 5; i++) { await page.click(".pick:not(.on) input"); await page.waitForTimeout(100); }
  const table = await page.$$eval("#cgrp option", o => o.find(x => /THD in frequency bands/.test(x.textContent)).value);
  await page.selectOption("#cgrp", table);
  await page.waitForSelector("#cchart");
  assert.ok((await page.$$("[data-row]")).length >= 2, "row buttons for a table measurement");
  await page.click('[data-src="diyAudio"]');
  await page.fill("#cfilt", "zzzz");
  assert.match(await page.textContent(".picks"), /no driver/i);
  assert.deepEqual(errors, []);
  await close();
});

test("Simulate: 2-, 3- and 4-way with every crossover type", { skip: skip() }, async () => {
  const { page, errors, close } = await open("#simulate");
  await page.waitForSelector("#schart");
  for (const n of [2, 4, 3]) {
    await page.click(`[data-n="${n}"]`);
    await page.waitForSelector("#schart");
    assert.equal((await page.$$("[data-way]")).length, n);
    assert.equal((await page.$$("[data-xf]")).length, n - 1);
  }
  for (const t of ["LR2", "LR8", "BW1", "BW2", "BW3", "BW4", "LR4"]) {
    await page.selectOption('[data-xt="0"]', t);
    await page.waitForSelector("#schart");
    assert.ok((await page.$$("#ssum tr")).length >= 2, t);
  }
  await page.fill("#sL", "104"); await page.press("#sL", "Enter");
  await page.waitForSelector("#schart");
  assert.match(await page.textContent(".ptitle"), /104 dB/);
  await page.fill("#sL", "999"); await page.press("#sL", "Enter");
  await page.waitForSelector("#schart");
  assert.match(await page.textContent(".warn"), /60 to 125/, "an out-of-range level is refused with a message");
  assert.match(await page.textContent(".ptitle"), /104 dB/, "and the old level is kept");
  await page.click('[data-ssrc="HiFiCompass"]');
  await page.waitForSelector("#schart");
  const [download] = await Promise.all([page.waitForEvent("download"), page.click(".exportrow [data-dl]")]);
  assert.match(download.suggestedFilename(), /^simulation_/);
  assert.deepEqual(errors, []);
  await close();
});

for (const [name, size] of Object.entries(SIZES)) {
  test(`No sideways scrolling and usable controls at ${name} (${size.join("×")})`, { skip: skip() }, async () => {
    for (const hash of ["", "#driver/purifi-ptt8-0x04-nab-02?src=HiFiCompass", "#driver/at-c-quenze-18-h-52-17-06-sd", "#compare", "#compare?src=diyAudio&g=diyAudio%3A%3Aimd-spectrum%7C40%2B96&q=products", "#simulate?n=4"]) {
      const { page, errors, close } = await open(hash, size);
      await page.waitForTimeout(300);
      assert.ok(await noSidewaysScroll(page), `${hash || "list"} scrolls sideways at ${name}`);
      // every control a finger has to hit: at least 32 px tall (a tick box counts with its label)
      const small = await page.$$eval("button, select, input, summary, .tabs a", els => els
        .map(e => (e.type === "checkbox" && e.closest("label")) || e)
        .filter(e => e.offsetParent !== null && e.getBoundingClientRect().height > 0 && e.getBoundingClientRect().height < 32)
        .map(e => e.tagName + "." + e.className + " " + Math.round(e.getBoundingClientRect().height) + "px " + (e.textContent || e.value || "").trim().slice(0, 30)));
      assert.deepEqual([...new Set(small)], [], `controls shorter than 32 px at ${name} on ${hash || "list"}`);
      if (hash !== "") assert.ok((await chartCount(page)) >= 1, `${hash} draws a chart at ${name}`);
      assert.deepEqual(errors, [], hash);
      await close();
    }
  });
}
