async (page) => {
  const origin = page.contosoGuideOrigin || "http://127.0.0.1:8765";
  const errors = [];
  const failedRequests = [];
  const checks = [];
  const check = (condition, name) => {
    if (!condition) throw new Error(`FAIL: ${name}`);
    checks.push(name);
  };
  const onError = error => errors.push(error.message);
  const onResponse = response => {
    if (response.status() >= 400) failedRequests.push(`${response.status()} ${response.url()}`);
  };
  page.on("pageerror", onError);
  page.on("response", onResponse);
  await page.setViewportSize({width: 1440, height: 1000});
  await page.goto(`${origin}/index.html#l00`);
  await page.waitForLoadState("networkidle");
  const originalState = await page.evaluate(() => localStorage.getItem("foundry-lab-guide-20260929"));
  try {
    await page.evaluate(() => localStorage.setItem(
      "foundry-lab-guide-20260929", JSON.stringify({done: [], theme: "light", path: "all"})
    ));
    await page.reload();
    await page.waitForLoadState("networkidle");
    check(await page.locator("article.chapter").count() === 30, "30 generated pages");
    check(await page.locator("[data-complete]").count() === 25, "25 trackable labs");
    check(await page.locator(".chapter.active").getAttribute("id") === "l00", "home route");
    check(await page.locator("html").getAttribute("lang") === "ko", "Korean language metadata");
    check(await page.locator('script[src^="http"],link[href^="http"]').count() === 0, "no remote runtime dependencies");
    const bodyText = await page.locator("body").textContent();
    check(bodyText.includes("Contoso") && !bodyText.includes("한빛") && !bodyText.includes("Hanbit"), "current scenario is consistently Contoso");

    const search = page.getByLabel("가이드 검색", {exact: true});
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
    await page.getByLabel("학습 경로", {exact: true}).selectOption("quick");
    const quick = await page.locator(".chapter-link:visible").evaluateAll(nodes => nodes.map(node => node.dataset.chapter));
    check(quick.join(",") === "l00,l01,l04,l05,l08,l12,instructor", "90-minute path matches the instructor schedule");
    await page.getByLabel("학습 경로", {exact: true}).selectOption("all");
    await page.locator('.chapter-link[data-chapter="l06"]').click();
    await page.locator('[data-complete="l06"]').click();
    check(await page.locator("#progress-label").innerText() === "1 / 25", "progress increments");
    await page.reload();
    check(await page.locator('[data-complete="l06"]').getAttribute("aria-pressed") === "true", "progress survives reload");
    check(await page.locator(".chapter.active").getAttribute("id") === "l06", "deep-link survives reload");
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
      await page.goto(`${origin}/index.html#l08`);
      const measure = await page.evaluate(() => ({
        viewport: innerWidth,
        document: document.documentElement.scrollWidth,
        prose: parseFloat(getComputedStyle(document.querySelector(".chapter.active .prose")).fontSize),
        code: parseFloat(getComputedStyle(document.querySelector(".chapter.active pre code")).fontSize),
      }));
      check(measure.document <= measure.viewport + 1, `no document overflow at ${width}px`);
      check(measure.prose >= 16, `body text >= 16px at ${width}px`);
      check(measure.code >= 13, `code text >= 13px at ${width}px`);
    }
    await page.setViewportSize({width: 390, height: 844});
    await page.locator("#menu-toggle").click();
    check(await page.locator("#menu-toggle").getAttribute("aria-expanded") === "true", "mobile menu opens");
    await page.locator('.chapter-link[data-chapter="l19"]').click();
    await page.locator("#l19.active").waitFor({state: "visible"});
    check(await page.locator(".chapter.active").getAttribute("id") === "l19", "mobile navigation");
    check(await page.locator("#menu-toggle").getAttribute("aria-expanded") === "false", "mobile menu closes after navigation");

    await page.setViewportSize({width: 1440, height: 1000});
    for (let index = 0; index < 25; index += 1) {
      const id = `l${String(index).padStart(2, "0")}`;
      await page.goto(`${origin}/index.html#${id}`);
      await page.locator(`#${id}.active`).waitFor({state: "visible"});
      check(await page.locator(".chapter.active").getAttribute("id") === id, `direct route ${id}`);
    }
    await page.goto(`${origin}/index.html#coverage`);
    check(await page.locator("#coverage tbody tr").count() === 95, "91 coverage rows plus 4 depth definitions");
    await page.goto(`${origin}/index.html#l05`);
    await page.emulateMedia({media: "print"});
    await page.evaluate(() => { document.body.dataset.print = "one"; });
    check(await page.locator(".chapter:visible").count() === 1, "single-module print");
    await page.evaluate(() => { document.body.dataset.print = "all"; });
    check(await page.locator(".chapter:visible").count() === 30, "complete-book print");
    await page.emulateMedia({media: null});
    await page.evaluate(() => { delete document.body.dataset.print; });
    await page.goto(`${origin}/index.html#%E0%A4%A`);
    check(await page.locator(".chapter.active").getAttribute("id") === "l00", "malformed hash has a safe fallback");

    const context = await page.context().browser().newContext({javaScriptEnabled: false});
    try {
      const nojs = await context.newPage();
      await nojs.goto(`${origin}/index.html`);
      check(await nojs.locator(".chapter:visible").count() === 30, "all content readable without JavaScript");
    } finally {
      await context.close();
    }
    check(errors.length === 0, "no browser runtime errors");
    check(failedRequests.length === 0, "no failed local assets");
    return {status: "passed", checks: checks.length, widths, assertions: checks, errors, failedRequests, azure_calls: 0};
  } finally {
    await page.emulateMedia({media: null});
    await page.goto(`${origin}/index.html#l00`);
    await page.evaluate(saved => {
      if (saved === null) localStorage.removeItem("foundry-lab-guide-20260929");
      else localStorage.setItem("foundry-lab-guide-20260929", saved);
    }, originalState);
    await page.reload();
    page.off("pageerror", onError);
    page.off("response", onResponse);
  }
}
