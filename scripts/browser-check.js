async (page) => {
  const origin = page.contosoGuideOrigin || "http://127.0.0.1:8765";
  const edition = page.contosoGuideEdition;
  const entry = `${origin}/${edition.html}`;
  const english = edition.language === "en";
  const errors = [];
  const failedRequests = [];
  const remoteRequests = [];
  const checks = [];
  const check = (condition, name) => {
    if (!condition) throw new Error(`FAIL: ${name}`);
    checks.push(name);
  };
  const onError = error => errors.push(error.message);
  const onResponse = response => {
    if (response.status() >= 400) failedRequests.push(`${response.status()} ${response.url()}`);
  };
  check(["127.0.0.1", "localhost", "[::1]"].includes(new URL(origin).hostname), "browser checks use a local origin");
  check(/^[\w.-]+\.json$/.test(edition.portal_manifest), "capture manifest is a local content filename");
  const localOnly = async route => {
    if (new URL(route.request().url()).origin !== new URL(origin).origin) {
      remoteRequests.push(route.request().url());
      await route.abort("blockedbyclient");
    } else {
      await route.continue();
    }
  };
  await page.route("**/*", localOnly);
  page.on("pageerror", onError);
  page.on("response", onResponse);
  await page.setViewportSize({width: 1440, height: 1000});
  await page.goto(`${entry}#l00`);
  await page.waitForLoadState("networkidle");
  const originalState = await page.evaluate(() => localStorage.getItem("foundry-lab-guide-20260929"));
  try {
    await page.evaluate(() => localStorage.setItem(
      "foundry-lab-guide-20260929", JSON.stringify({done: [], theme: "light", path: "all"})
    ));
    await page.reload();
    await page.waitForLoadState("networkidle");
    check(await page.locator("article.chapter").count() === 30, "30 generated pages");
    check(await page.locator('.chapter[data-track="advanced"] .learning-badge').count() === 12, "all advanced modules show execution dependency labels");
    check(await page.locator('#l14 .learning-badge').innerText() === (english ? "Prerequisites required" : "선행 실습 필요"), "Hosted prerequisite is explicit");
    check(await page.locator('#l16 .learning-badge').innerText() === (english ? "Independent elective" : "독립 선택"), "Memory is marked independently selectable");
    check(await page.locator('#l20 .learning-badge').innerText() === (english ? "Separate feature paths" : "기능별 분기"), "Optimizer and fine-tuning paths are distinguished");
    check(await page.locator(".nav-learning").count() === 12, "advanced navigation exposes dependency labels");
    check(await page.locator("[data-complete]").count() === 25, "25 trackable labs");
    check(await page.locator('.chapter:not([data-track="reference"]) .prose h2').filter({hasText: english ? "Concepts and lab map" : "개념과 실습 지도"}).count() === 25, "all 25 labs explain feature, purpose, method and execution surface");
    check(await page.locator(".command-explanation").count() === edition.shell_blocks, `all ${edition.shell_blocks} shell blocks have visible command explanations`);
    check(await page.locator(".command-explanation tbody tr").count() === edition.commands, `all ${edition.commands} logical CLI commands have individual explanation rows`);
    const captures = await page.evaluate(async ({english, edition}) => {
      const response = await fetch(`content/${edition.portal_manifest}`);
      if (!response.ok) throw new Error(`Missing capture manifest: ${edition.portal_manifest}`);
      const manifest = await response.json();
      const directory = english ? "assets/portal/en/" : "assets/portal/";
      if (!manifest.captures.every(item =>
        item.path.startsWith(directory) && /^\d{2}-[a-z0-9-]+\.png$/.test(item.path.slice(directory.length))
      )) throw new Error("Portal captures must use this language's local image directory.");
      const hashes = await Promise.all(manifest.captures.map(async item => {
        const response = await fetch(item.path);
        if (!response.ok) throw new Error(`Missing portal capture: ${item.path}`);
        const hash = await crypto.subtle.digest("SHA-256", await response.arrayBuffer());
        return [...new Uint8Array(hash)].map(value => value.toString(16).padStart(2, "0")).join("") === item.sha256;
      }));
      const images = [...document.querySelectorAll('img[src^="assets/portal/"]')];
      return {
        declared: manifest.captures.map(item => item.path).sort(),
        rendered: [...new Set(images.map(image => image.getAttribute("src")))].sort(),
        genuine: manifest.capture_method === "playwright-mcp-headless" && manifest.synthetic_ui === false,
        scoped: manifest.scope?.repository_id === 1396573688 &&
          manifest.scope?.project === (english ? "contoso-workshop-en" : "contoso-workshop") &&
          Boolean(manifest.scope?.resource_group && manifest.scope?.ownership_receipt),
        provenance: manifest.captures.every(item =>
          item.route && item.purpose && item.masked?.length &&
          /(?:Z|[+-]\d{2}:\d{2})$/.test(item.captured_at) && Number.isFinite(Date.parse(item.captured_at))
        ),
        hashesMatch: hashes.every(Boolean),
        loaded: images.every(image => image.complete && image.naturalWidth > 0),
        captioned: images.every(image => image.closest(".portal-capture")?.textContent.includes(english ? "Not deployment or quality evidence" : "배포·품질 검증과 구분")),
      };
    }, {english, edition});
    check(captures.declared.length === edition.portal_screenshots && JSON.stringify(captures.declared) === JSON.stringify(captures.rendered), "language-specific portal capture manifest matches the rendered guide");
    check(captures.genuine && captures.scoped && captures.provenance && captures.hashesMatch, "all portal captures retain genuine scoped provenance and original hashes");
    check(captures.loaded && captures.captioned, "all offline portal images load with provenance and execution boundaries");
    for (const path of [edition.receipt_html, edition.validation]) {
      check(await page.locator(`.site-footer a[href="${path}"]`).count() === 1, `footer uses localized link: ${path}`);
      check(await page.locator(`.print-cover a[href="${path}"]`).count() === 1, `print cover uses localized link: ${path}`);
      const response = await page.request.get(`${origin}/${path}`);
      check(response.ok(), `localized receipt/evidence file is available: ${path}`);
      if (path === edition.receipt_html) {
        check((await response.text()).includes(`<html lang="${edition.language}">`), "synthetic receipt matches the reader language");
      }
    }
    for (const source of ["samples/workshop.py", "azure.yaml", ".env.example", ".github/workflows/validate.yml"]) {
      const response = await page.request.get(`${origin}/${source}`);
      check(response.ok() && response.headers()["content-type"].startsWith("text/plain"), `source is readable as text: ${source}`);
    }
    check(await page.locator(".chapter.active").getAttribute("id") === "l00", "home route");
    check(await page.locator("html").getAttribute("lang") === edition.language, "correct language metadata");
    check(await page.locator('script[src^="http"],link[rel="stylesheet"][href^="http"]').count() === 0, "no remote runtime dependencies");
    check(await page.locator('.language-switch a[aria-current="true"]').getAttribute("lang") === edition.language, "current language is accessible");
    const rootResponse = await page.request.get(`${origin}/`);
    check((await rootResponse.text()).includes('<html lang="en">'), "site root defaults to English");
    const bodyText = await page.locator("body").textContent();
    check(bodyText.includes("Contoso") && !bodyText.includes("한빛") && !bodyText.includes("Hanbit"), "current scenario is consistently Contoso");
    const icon = await page.locator(".brand img").evaluate(image => ({
      source: image.getAttribute("src"), loaded: image.complete && image.naturalWidth > 0,
      fit: getComputedStyle(image).objectFit, width: image.width, height: image.height,
    }));
    check(icon.loaded && icon.source === "assets/microsoft-foundry.svg", "official Foundry icon loads from the offline kit");
    check(icon.fit === "contain" && icon.width === icon.height, "official icon keeps its original aspect ratio");
    const iconHash = await page.evaluate(async () => {
      const bytes = await (await fetch("assets/microsoft-foundry.svg")).arrayBuffer();
      const hash = await crypto.subtle.digest("SHA-256", bytes);
      return [...new Uint8Array(hash)].map(value => value.toString(16).padStart(2, "0")).join("");
    });
    check(iconHash === "fab039a771f72780ae34e59065d61c66a02d3c347d50923ef2956f34912ea02c", "official icon bytes match Microsoft's V24 distribution");

    const search = page.locator("#guide-search");
    await search.fill("Foundry IQ");
    check(await page.locator("#search-results").isVisible(), "search opens a result view");
    check(await page.locator('.search-result[href="#l13"]').count() === 1, "search finds the IQ lab");
    await page.locator('.search-result[href="#l13"]').click();
    await page.locator("#l13.active").waitFor({state: "visible"});
    check(await page.locator(".chapter.active").getAttribute("id") === "l13", "search result navigation");
    check(await search.inputValue() === "", "search clears on navigation");
    await search.fill("zzznomatch829107");
    check(await page.locator(".search-result").count() === 0, "empty search result is explicit");
    await search.press("Escape");
    await page.locator("#l13.active").waitFor({state: "visible"});
    check(await page.locator(".chapter.active").getAttribute("id") === "l13", "Escape restores reading");
    await page.locator("#learning-path").selectOption("quick");
    const quick = await page.locator(".chapter-link:visible").evaluateAll(nodes => nodes.map(node => node.dataset.chapter));
    check(quick.join(",") === "l00,l01,l04,l05,l08,l12,instructor", "90-minute path matches the instructor schedule");
    await page.locator("#learning-path").selectOption("all");
    await page.locator('.chapter-link[data-chapter="l06"]').click();
    await page.locator('[data-complete="l06"]').click();
    check(await page.locator("#progress-label").innerText() === "1 / 25", "progress increments");
    await page.reload();
    check(await page.locator('[data-complete="l06"]').getAttribute("aria-pressed") === "true", "progress survives reload");
    check(await page.locator(".chapter.active").getAttribute("id") === "l06", "deep-link survives reload");
    const other = english ? "ko" : "en";
    await page.locator(`.language-switch [data-language="${other}"]`).click();
    await page.locator("#l06.active").waitFor({state: "visible"});
    check(await page.locator("html").getAttribute("lang") === other, "language switch opens the other edition");
    check(await page.locator('[data-complete="l06"]').getAttribute("aria-pressed") === "true", "progress is shared across languages");
    check(await page.locator(".chapter.active").getAttribute("id") === "l06", "language switch preserves the current module");
    await page.locator(`.language-switch [data-language="${edition.language}"]`).click();
    await page.locator("#l06.active").waitFor({state: "visible"});
    await page.locator('[data-complete="l06"]').click();

    await page.evaluate(() => {
      Object.defineProperty(navigator, "clipboard", {
        configurable: true,
        value: {writeText: async text => { window.__workshopCopiedText = text; }},
      });
    });
    const expectedCode = await page.locator("#l06 pre code").first().textContent();
    await page.locator("#l06 .copy-button").first().click();
    check(await page.evaluate(() => window.__workshopCopiedText) === expectedCode, "copy includes code only, not labels");
    await page.evaluate(() => {
      Object.defineProperty(navigator, "clipboard", {
        configurable: true, value: {writeText: async () => { throw new Error("test-denied"); }},
      });
    });
    await page.locator("#l06 .copy-button").first().click();
    const selectedCode = await page.evaluate(() => window.getSelection().toString());
    check(selectedCode.trimEnd() === expectedCode.trimEnd(), "copy denial selects code for manual copy");

    for (const theme of ["dark", "light"]) {
      await page.locator("#theme-toggle").click();
      check(await page.locator("html").getAttribute("data-theme") === theme, `${theme} theme toggle`);
      const ratios = await page.evaluate(() => {
        const styles = getComputedStyle(document.documentElement);
        const luminance = value => {
          const hex = value.trim().slice(1);
          const channels = [0, 2, 4].map(index => parseInt(hex.slice(index, index + 2), 16) / 255);
          const linear = channels.map(value => value <= .04045 ? value / 12.92 : ((value + .055) / 1.055) ** 2.4);
          return linear[0] * .2126 + linear[1] * .7152 + linear[2] * .0722;
        };
        return [["--text", "--surface"], ["--muted", "--surface"], ["--accent", "--surface"], ["--amber", "--amber-soft"]].map(([fg, bg]) => {
          const a = luminance(styles.getPropertyValue(fg)), b = luminance(styles.getPropertyValue(bg));
          return {pair: `${fg}/${bg}`, ratio: (Math.max(a, b) + .05) / (Math.min(a, b) + .05)};
        });
      });
      check(ratios.every(item => item.ratio >= 4.5), `${theme} primary text contrast >= 4.5:1`);
    }

    const widths = [1440, 1024, 768, 390, 320];
    for (const width of widths) {
      await page.setViewportSize({width, height: 900});
      await page.goto(`${entry}#l08`);
      const measure = await page.evaluate(() => ({
        viewport: innerWidth,
        document: document.documentElement.scrollWidth,
        prose: parseFloat(getComputedStyle(document.querySelector(".chapter.active .prose")).fontSize),
        code: parseFloat(getComputedStyle(document.querySelector(".chapter.active pre code")).fontSize),
        navigation: parseFloat(getComputedStyle(document.querySelector(".chapter-link")).fontSize),
        table: parseFloat(getComputedStyle(document.querySelector(".chapter.active td")).fontSize),
        brandRight: document.querySelector(".brand").getBoundingClientRect().right,
        actionsLeft: document.querySelector(".top-actions").getBoundingClientRect().left,
      }));
      check(measure.document <= measure.viewport + 1, `no document overflow at ${width}px`);
      check(measure.prose >= 18, `body text >= 18px at ${width}px`);
      check(measure.code >= 14, `code text >= 14px at ${width}px`);
      check(measure.navigation >= 14, `navigation text >= 14px at ${width}px`);
      check(measure.table >= 14, `table text >= 14px at ${width}px`);
      check(measure.brandRight <= measure.actionsLeft, `brand and header controls do not overlap at ${width}px`);
      check(await page.locator(`.language-switch [data-language="${other}"]`).isVisible(), `language switch remains available at ${width}px`);
      await page.goto(`${entry}#l04`);
      const imageBounds = await page.locator("#l04 .portal-capture img").evaluateAll(images => images.map(image => ({
        width: image.getBoundingClientRect().width,
        container: image.closest("figure").getBoundingClientRect().width,
        loaded: image.complete && image.naturalWidth > 0,
      })));
      check(imageBounds.length > 0 && imageBounds.every(image => image.loaded && image.width <= image.container + 1), `portal screenshots fit the reader at ${width}px`);
    }
    await page.setViewportSize({width: 390, height: 844});
    await page.locator("#menu-toggle").click();
    check(await page.locator("#menu-toggle").getAttribute("aria-expanded") === "true", "mobile menu opens");
    await page.locator('.chapter-link[data-chapter="l19"]').click();
    await page.locator("#l19.active").waitFor({state: "visible"});
    check(await page.locator(".chapter.active").getAttribute("id") === "l19", "mobile navigation");
    check(await page.locator("#menu-toggle").getAttribute("aria-expanded") === "false", "mobile menu closes after navigation");
    await page.locator(".brand").click();
    await page.locator("#l00.active").waitFor({state: "visible"});
    check(await page.locator(".chapter.active").getAttribute("id") === "l00", "official brand icon still links to the start");

    await page.setViewportSize({width: 1440, height: 1000});
    for (let index = 0; index < 25; index += 1) {
      const id = `l${String(index).padStart(2, "0")}`;
      await page.goto(`${entry}#${id}`);
      await page.locator(`#${id}.active`).waitFor({state: "visible"});
      check(await page.locator(".chapter.active").getAttribute("id") === id, `direct route ${id}`);
    }
    await page.goto(`${entry}#coverage`);
    check(await page.locator("#coverage tbody tr").count() === 95, "91 coverage rows plus 4 depth definitions");
    await page.goto(`${entry}#l05`);
    await page.emulateMedia({media: "print"});
    await page.evaluate(() => { document.body.dataset.print = "one"; });
    check(await page.locator(".chapter:visible").count() === 1, "single-module print");
    await page.evaluate(() => { document.body.dataset.print = "all"; });
    check(await page.locator(".chapter:visible").count() === 30, "complete-book print");
    const printFonts = await page.evaluate(() => ({
      prose: parseFloat(getComputedStyle(document.querySelector("#l05 .prose")).fontSize),
      code: parseFloat(getComputedStyle(document.querySelector("#l05 pre code")).fontSize),
    }));
    check(printFonts.prose >= 14.66, "PDF body text >= 11pt");
    check(printFonts.code >= 12, "PDF code text >= 9pt");
    await page.emulateMedia({media: null});
    await page.evaluate(() => { delete document.body.dataset.print; });
    await page.goto(`${entry}#%E0%A4%A`);
    check(await page.locator(".chapter.active").getAttribute("id") === "l00", "malformed hash has a safe fallback");

    const context = await page.context().browser().newContext({javaScriptEnabled: false});
    try {
      await context.route("**/*", localOnly);
      const nojs = await context.newPage();
      await nojs.goto(entry);
      check(await nojs.locator(".chapter:visible").count() === 30, "all content readable without JavaScript");
      await nojs.locator(`.language-switch [data-language="${other}"]`).click();
      check(await nojs.locator("html").getAttribute("lang") === other, "language switching works without JavaScript");
    } finally {
      await context.close();
    }
    check(errors.length === 0, "no browser runtime errors");
    check(failedRequests.length === 0, "no failed local assets");
    check(remoteRequests.length === 0, "no remote browser network requests");
    return {status: "passed", language: edition.language, checks: checks.length, widths, assertions: checks, errors, failedRequests, remoteRequests, azure_calls: 0};
  } finally {
    await page.emulateMedia({media: null});
    await page.goto(`${entry}#l00`);
    await page.evaluate(saved => {
      if (saved === null) localStorage.removeItem("foundry-lab-guide-20260929");
      else localStorage.setItem("foundry-lab-guide-20260929", saved);
    }, originalState);
    await page.reload();
    page.off("pageerror", onError);
    page.off("response", onResponse);
    await page.unroute("**/*", localOnly);
  }
}
