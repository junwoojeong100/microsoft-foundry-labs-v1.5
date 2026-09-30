"use strict";

const fs = require("node:fs/promises");
const http = require("node:http");
const path = require("node:path");
const vm = require("node:vm");
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
  const { values, positionals } = parseArgs({
    options: { "report-dir": { type: "string", default: "validation/current" } },
    allowPositionals: true,
  });
  const [operation] = positionals;
  if (positionals.length !== 1 || !["check", "pdf"].includes(operation)) throw new Error("Use check or pdf [--report-dir validation/PATH].");
  const reportDir = path.resolve(root, values["report-dir"]);
  if (!reportDir.startsWith(path.join(root, "validation") + path.sep)) throw new Error("Reports must be inside validation/.");
  const server = http.createServer(async (request, response) => {
    try {
      const pathname = decodeURIComponent(new URL(request.url, "http://127.0.0.1").pathname);
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
    page.contosoGuideOrigin = `http://127.0.0.1:${server.address().port}`;
    const privateResponse = await fetch(`${page.contosoGuideOrigin}/.env`);
    if (privateResponse.status !== 403) throw new Error("Private environment files must never be served.");
    const filename = operation === "check" ? "browser-check.js" : "export-pdf.js";
    const callback = vm.runInThisContext(await fs.readFile(path.join(__dirname, filename), "utf8"), { filename });
    const result = await callback(page);
    result.private_paths_blocked = true;
    if (operation === "check") {
      await fs.mkdir(reportDir, { recursive: true });
      await fs.writeFile(path.join(reportDir, "browser.json"), JSON.stringify(result, null, 2) + "\n");
      await page.screenshot({ path: path.join(reportDir, "desktop.png") });
      await page.setViewportSize({ width: 390, height: 844 });
      await page.screenshot({ path: path.join(reportDir, "mobile.png") });
    }
    console.log(JSON.stringify(result, null, 2));
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
