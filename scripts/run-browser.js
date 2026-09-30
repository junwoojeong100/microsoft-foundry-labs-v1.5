"use strict";

const fs = require("node:fs/promises");
const http = require("node:http");
const path = require("node:path");
const vm = require("node:vm");
const { chromium } = require("playwright");
const root = path.resolve(__dirname, "..");
const types = { ".html": "text/html; charset=utf-8", ".svg": "image/svg+xml", ".json": "application/json", ".css": "text/css", ".js": "text/javascript" };

async function main() {
  const operation = process.argv[2];
  if (!["check", "pdf"].includes(operation)) throw new Error("Use check or pdf.");
  const server = http.createServer(async (request, response) => {
    try {
      const pathname = decodeURIComponent(new URL(request.url, "http://127.0.0.1").pathname);
      const privatePath = pathname.split("/").some(part =>
        part.startsWith(".") && part !== ".env.example" || ["results", "node_modules"].includes(part));
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
      await fs.mkdir(path.join(root, "validation/current"), { recursive: true });
      await fs.writeFile(path.join(root, "validation/current/browser.json"), JSON.stringify(result, null, 2) + "\n");
      await page.screenshot({ path: path.join(root, "validation/current/desktop.png") });
      await page.setViewportSize({ width: 390, height: 844 });
      await page.screenshot({ path: path.join(root, "validation/current/mobile.png") });
    }
    console.log(JSON.stringify(result, null, 2));
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
