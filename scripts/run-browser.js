"use strict";

const fs = require("node:fs/promises");
const http = require("node:http");
const path = require("node:path");
const vm = require("node:vm");
const { createHash } = require("node:crypto");
const { parseArgs } = require("node:util");
const { chromium } = require("playwright");
const root = path.resolve(__dirname, "..");
const types = {
  ".html": "text/html; charset=utf-8", ".svg": "image/svg+xml", ".png": "image/png",
  ".json": "application/json", ".css": "text/css", ".js": "text/javascript",
  ...Object.fromEntries([".py", ".md", ".txt", ".yaml", ".yml", ".bicep", ".csv", ".jsonl", ".example"].map(
    extension => [extension, "text/plain; charset=utf-8"]
  )),
};
const publicSources = new Set(["/.env.example", "/.github/workflows/validate.yml", "/.github/workflows/azure-validation.yml"]);

async function main() {
  const release = JSON.parse(await fs.readFile(path.join(root, "content/release.json"), "utf8"));
  const { values, positionals } = parseArgs({
    options: { "report-dir": { type: "string", default: release.documentation_validation } },
    allowPositionals: true,
  });
  const [operation] = positionals;
  if (positionals.length !== 1 || operation !== "check") throw new Error("Use check [--report-dir results/PATH].");
  const reportDir = path.resolve(root, values["report-dir"]);
  if (!reportDir.startsWith(path.join(root, "results") + path.sep)) throw new Error("Reports must be inside private results/.");
  const sitePath = new URL(release.site_url).pathname.replace(/\/$/, "");
  const server = http.createServer(async (request, response) => {
    try {
      const requestPath = decodeURIComponent(new URL(request.url, "http://127.0.0.1").pathname);
      if (!requestPath.startsWith(sitePath + "/")) { response.writeHead(404).end("Unknown site"); return; }
      const pathname = requestPath.slice(sitePath.length);
      const privatePath = !publicSources.has(pathname) && pathname.split("/").some(part =>
        part.startsWith(".") || ["results", "node_modules"].includes(part));
      if (privatePath) { response.writeHead(403).end("Private path"); return; }
      const file = path.resolve(root, "." + (pathname === "/" ? "/index.html" : pathname));
      if (!file.startsWith(root + path.sep)) { response.writeHead(403).end(); return; }
      const data = await fs.readFile(file);
      response.writeHead(200, { "Content-Type": types[path.extname(file)] || "application/octet-stream" });
      response.end(data);
    } catch (error) {
      console.error("Guide asset request failed:", error.code || error.name);
      response.writeHead(404).end("Not found");
    }
  });
  await new Promise((resolve, reject) => { server.once("error", reject); server.listen(0, "127.0.0.1", resolve); });
  let browser;
  try {
    browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    page.contosoGuideOrigin = `http://127.0.0.1:${server.address().port}${sitePath}`;
    const privateResponse = await fetch(`${page.contosoGuideOrigin}/.env`);
    if (privateResponse.status !== 403) throw new Error("Private environment files must never be served.");
    const filename = "browser-check.js";
    const callback = vm.runInThisContext(await fs.readFile(path.join(__dirname, filename), "utf8"), { filename });
    const result = {
      checked_at: new Date().toISOString(),
      scope: "Local bilingual documentation only; no Azure execution.",
      private_paths_blocked: true,
      default_language: release.default_language,
      languages: {},
    };
    for (const [language, edition] of Object.entries(release.languages)) {
      page.contosoGuideEdition = { ...edition, language };
      page.contosoGuideRelease = release;
      const checked = await callback(page);
      checked.guide_sha256 = createHash("sha256").update(await fs.readFile(path.join(root, edition.html))).digest("hex");
      result.languages[language] = checked;
      const screenshotDir = language === release.default_language ? reportDir : path.join(reportDir, language);
      await fs.mkdir(screenshotDir, { recursive: true });
      await page.setViewportSize({ width: 1440, height: 1000 });
      await page.screenshot({ path: path.join(screenshotDir, "desktop.png") });
      await page.setViewportSize({ width: 390, height: 844 });
      await page.screenshot({ path: path.join(screenshotDir, "mobile.png") });
    }
    await fs.writeFile(path.join(reportDir, "browser.json"), JSON.stringify(result, null, 2) + "\n");
    console.log(JSON.stringify(result, null, 2));
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
