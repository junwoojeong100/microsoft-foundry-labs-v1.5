async (page) => {
  page.setDefaultTimeout(30000);
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
  check(/^[\w.-]+\.json$/.test(page.contosoGuideRelease.portal_step_manifest), "numbered-screen manifest is a local content filename");
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
  const chapters = await page.evaluate(async () => {
    const response = await fetch("content/chapters.json");
    if (!response.ok) throw new Error("Missing curriculum manifest.");
    return response.json();
  });
  const labIds = chapters.filter(chapter => chapter.track !== "reference").map(chapter => chapter.id);
  const expectedLabIds = [...Array.from({length: 11}, (_, index) => `l${String(index).padStart(2, "0")}`),
    "l13", "l14", "l15", "l15-collaboration", "l16", "l17", "l21", "l22", "l12"];
  const expectedNumbers = Array.from({length: 20}, (_, index) => String(index).padStart(2, "0"));
  const corePathCount = chapters.filter(chapter => ["core", "wrapup"].includes(chapter.track)).length;
  const advancedCount = chapters.filter(chapter => chapter.track === "advanced").length;
  const advancedPathCount = chapters.filter(chapter => ["advanced", "wrapup"].includes(chapter.track)).length;
  const practiceIds = ["l15", "l15-collaboration", "l21", "l22"];
  const terminalIds = ["l14", "l15", "l15-collaboration"];
  const diagrams = {
    l14: "assets/hosted-lifecycle.svg", l15: "assets/maf-patterns.svg",
    "l15-collaboration": "assets/maf-collaboration.svg",
  };
  check(JSON.stringify(page.contosoGuideRelease.terminal_labs) === JSON.stringify(terminalIds),
    "only Hosted and the two MAF modules authorize terminal execution");
  check(JSON.stringify(labIds) === JSON.stringify(expectedLabIds), "the 20-lab curriculum consolidates capstone and ends with shared wrap-up");
  check(JSON.stringify(chapters.filter(chapter => chapter.track !== "reference").map(chapter => chapter.number)) === JSON.stringify(expectedNumbers),
    "learner-facing module numbers are continuous from 00 through 19");
  const originalState = await page.evaluate(() => localStorage.getItem("foundry-lab-guide-20260929"));
  try {
    await page.evaluate(() => localStorage.removeItem("foundry-lab-guide-20260929"));
    await page.reload();
    check(corePathCount === 12 && advancedPathCount === 9, "path counts include one shared wrap-up without duplicate modules");
    check(await page.locator("#learning-path").inputValue() === "core", "new readers start with 11 core modules plus wrap-up");
    check(await page.locator("#progress-label").innerText() === `0 / ${corePathCount}`, "new readers are not asked to complete every elective and core lab");
    check(await page.locator(".chapter-link:visible").count() === corePathCount, "default contents contain the core sequence and shared wrap-up");
    check(await page.locator(".reader-help a:visible").count() === 2, "glossary and troubleshooting remain available outside path filtering");
    await page.evaluate(() => localStorage.setItem(
      "foundry-lab-guide-20260929",
      JSON.stringify({done: ["l11", "l18", "l19", "l20", "l21", "l23", "l24"], theme: "light", path: "all"})
    ));
    await page.reload();
    check(await page.locator("#progress-label").innerText() === `1 / ${labIds.length}`, "saved progress excludes merged/removed IDs and retains the governance lab");
    check(await page.locator('[data-complete="l21"]').getAttribute("aria-pressed") === "true", "retained elective progress survives curriculum pruning");
    check(await page.locator('[data-complete="l15-collaboration"]').getAttribute("aria-pressed") === "false", "a merged capstone checkmark does not complete the new collaboration lab");
    await page.evaluate(() => localStorage.setItem(
      "foundry-lab-guide-20260929", JSON.stringify({done: [], theme: "light", path: "all"})
    ));
    await page.reload();
    await page.waitForLoadState("networkidle");
    check(JSON.stringify(await page.locator("article.chapter").evaluateAll(nodes => nodes.map(node => node.id))) === JSON.stringify(chapters.map(chapter => chapter.id)), "generated articles exactly match curriculum order");
    check(JSON.stringify(await page.locator('.chapter-link:not([data-track="reference"]) .nav-number').allTextContents()) === JSON.stringify(expectedNumbers),
      "full navigation displays the same continuous order as the reader");
    check(await page.locator('.chapter[data-track="advanced"] .learning-badge').count() === advancedCount, "all advanced modules show execution dependency labels");
    const learningPaths = await page.evaluate(async english => {
      const response = await fetch(`content/learning-paths${english ? ".en" : ""}.json`);
      if (!response.ok) throw new Error("Missing learning-path prerequisites.");
      return response.json();
    }, english);
    for (const [id, prerequisite] of Object.entries(learningPaths)) {
      check(await page.locator(`#${id} .learning-badge`).innerText() === prerequisite.label,
        `${id} displays its current portal execution boundary`);
    }
    check(await page.locator(".nav-learning").count() === advancedCount, "advanced navigation exposes dependency labels");
    check(await page.locator("[data-complete]").count() === labIds.length, "all active labs are trackable");
    check(await page.locator(".lab-brief").count() === labIds.length, "all active modules have beginner start cards");
    check(await page.locator(".lab-handoff").count() === labIds.length, "all active modules identify saved results and the next step");
    const portalOnly = '.chapter:not([data-track="reference"])' + terminalIds.map(id => `:not(#${id})`).join("");
    check(await page.locator(`${portalOnly} pre code:not(.language-prompt)`).count() === 0,
      "all seventeen portal modules remain free of executable code and environment files");
    for (const id of terminalIds) {
      check(await page.locator(`#${id} pre code.language-bash`).count() > 0
        && await page.locator(`#${id} .command-explanation`).count() > 0
        && await page.locator(`#${id} pre code.language-${id === "l14" ? "yaml" : "python"}`).count() > 0,
      `${id} exposes actual source and explained terminal commands rather than hidden references`);
    }
    check(await page.locator("pre code.language-prompt").count() === edition.prompt_blocks,
      `all ${edition.prompt_blocks} portal question blocks identify their input destination`);
    check(await page.locator("pre code.language-env").count() === edition.settings_blocks, "settings blocks are distinguished from terminal commands");
    check(await page.locator(".practice-block").count() === practiceIds.length, "four advanced modules expose a try-change-explain exercise");
    check(await page.locator('#l01 .operator-only').count() === 0,
      "participant provisioning is not hidden behind a separate persona");
    const setupText = await page.locator("#l01").innerText();
    check(["Resource groups", "Advanced options", "Log Analytics workspaces",
      "Application Insights", "Project Managed Identity", "View my access"].every(term => setupText.includes(term)),
      "portal setup names resource creation, existing-access inspection, and keyless logging actions");
    check(await page.locator('#l01 #l01-python, #l01 #l01-azure-cli, #l01 #l01-vscode, #l01 #l01-interpreter').count() === 4,
      "old installation bookmarks remain resolvable without retaining installation instructions");
    check(!/az login|pip install|python -m venv|scripts\/azure_environment\.py/.test(setupText),
      "learner setup does not require a terminal, SDK, or device-code command");
    check(await page.locator('.chapter:not([data-track="reference"]) .prose h2').filter({hasText: english ? "Concepts and lab map" : "개념과 실습 지도"}).count() === labIds.length, "all active labs explain feature, purpose, method and execution surface");
    check(await page.locator(".command-explanation").count() === edition.shell_blocks, `all ${edition.shell_blocks} shell blocks have visible command explanations`);
    check(await page.locator(".command-explanation tbody tr").count() === edition.commands, `all ${edition.commands} logical CLI commands have individual explanation rows`);
    const captures = await page.evaluate(async ({english, edition, stepManifest}) => {
      const response = await fetch(`content/${edition.portal_manifest}`);
      if (!response.ok) throw new Error(`Missing capture manifest: ${edition.portal_manifest}`);
      const manifest = await response.json();
      const stepResponse = await fetch(`content/${stepManifest}`);
      if (!stepResponse.ok) throw new Error("Missing numbered-screen provenance.");
      const steps = await stepResponse.json();
      const sourceResponse = await fetch("content/portal-recordings.json");
      if (!sourceResponse.ok) throw new Error("Missing source recording provenance.");
      const recordings = await sourceResponse.json();
      const directory = english ? "assets/portal/en/" : "assets/portal/";
      const allCaptures = [...manifest.captures, ...(manifest.archived_captures || [])];
      if (new Set(allCaptures.map(item => item.path)).size !== allCaptures.length) {
        throw new Error("Active and archived portal capture paths must be distinct.");
      }
      if (!allCaptures.every(item =>
        item.path.startsWith(directory) && /^\d{2}-[a-z0-9-]+\.png$/.test(item.path.slice(directory.length))
      )) throw new Error("Portal captures must use this language's local image directory.");
      if (!steps.frames.every(item => item.path === `assets/portal/steps/${item.id}.png`
          && /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(item.id))) {
        throw new Error("Numbered screens must use their reviewed local PNG paths.");
      }
      const hashes = await Promise.all([...allCaptures, ...steps.frames].map(async item => {
        const response = await fetch(item.path);
        if (!response.ok) throw new Error(`Missing portal capture: ${item.path}`);
        const hash = await crypto.subtle.digest("SHA-256", await response.arrayBuffer());
        return [...new Uint8Array(hash)].map(value => value.toString(16).padStart(2, "0")).join("") === item.sha256;
      }));
      const images = [...document.querySelectorAll('img[src^="assets/portal/"]')];
      const diagrams = [...document.querySelectorAll('img[src^="assets/maf-"], img[src="assets/hosted-lifecycle.svg"]')];
      const historical = images.filter(image => !image.getAttribute("src").startsWith("assets/portal/steps/"));
      const numbered = images.filter(image => image.getAttribute("src").startsWith("assets/portal/steps/"));
      const deferred = images.every(image =>
        image.loading === "lazy" && image.decoding === "async" && image.width > 0 && image.height > 0 &&
        image.getAttribute("width") && image.getAttribute("height")
      );
      // Figures load lazily in the reader; force them to load so offline availability is still verified.
      await Promise.all(images.map(image => { image.loading = "eager"; return image.decode().catch(() => {}); }));
      await Promise.all(diagrams.map(image => image.decode()));
      return {
        deferred,
        declared: manifest.captures.map(item => item.path).sort(),
        rendered: [...new Set(historical.map(image => image.getAttribute("src")))].sort(),
        framesDeclared: steps.frames.map(item => item.path).sort(),
        framesRendered: [...new Set(numbered.map(image => image.getAttribute("src")))].sort(),
        timedFrames: [steps.frames[0], ...steps.frames.filter(frame => [130.4, 180.9].includes(frame.seconds))],
        reviewedFrames: steps.capture_method === "ffmpeg-video-frame" && steps.synthetic_ui === false
          && steps.execution_language === "ko" && steps.privacy_review.status === "passed"
          && steps.privacy_review.images === steps.frames.length && steps.privacy_review.flags === 0
          && steps.privacy_review.ocr === "passed" && steps.privacy_review.visual === "passed"
          && steps.frames.every(frame => recordings.clips.some(clip =>
            clip.id === frame.clip && clip.sha256.mp4 === frame.source_sha256)),
        nativeSizes: numbered.every(image => {
          const frame = steps.frames.find(item => item.path === image.getAttribute("src"));
          return frame && image.naturalWidth === frame.crop_xywh[2] + frame.padding_ltrb[0] + frame.padding_ltrb[2]
            && image.naturalHeight === frame.crop_xywh[3] + frame.padding_ltrb[1] + frame.padding_ltrb[3];
        }),
        visualModules: [...document.querySelectorAll('article.chapter:not([data-track="reference"])')].map(chapter => ({
          id: chapter.id, cards: chapter.querySelectorAll(".screen-step").length,
          diagrams: [...chapter.querySelectorAll('img[src$=".svg"]')].filter(image =>
            image.complete && image.naturalWidth > 0 && image.alt
          ).map(image => image.getAttribute("src")),
          sourceBlocks: chapter.querySelectorAll("pre code.language-python, pre code.language-yaml").length,
          commandBlocks: chapter.querySelectorAll("pre code.language-bash").length,
          complete: [...chapter.querySelectorAll(".screen-step")].every(card => {
            const image = card.querySelector("img");
            const frame = steps.frames.find(item => item.path === image?.getAttribute("src"));
            const link = card.querySelector('a[href^="downloads/portal/index.html?"]');
            if (!frame || !link || !image.alt || !card.querySelector("p strong")) return false;
            const address = new URL(link.href);
            return address.searchParams.get("clip") === frame.clip
              && Number(address.searchParams.get("t")) === frame.seconds
              && address.searchParams.get("lang") === edition.language && address.hash === `#${frame.clip}`
              && image.closest("a.screen-image")?.getAttribute("href") === frame.path;
          }),
        })),
        genuine: manifest.capture_method === "playwright-mcp-headless" && manifest.synthetic_ui === false,
        scoped: manifest.scope?.repository_id === 1396573688 &&
          manifest.scope?.project === (english ? "contoso-workshop-en" : "contoso-workshop") &&
          Boolean(manifest.scope?.resource_group && manifest.scope?.ownership_receipt),
        provenance: allCaptures.every(item =>
          item.route && item.purpose && item.masked?.length &&
          /(?:Z|[+-]\d{2}:\d{2})$/.test(item.captured_at) && Number.isFinite(Date.parse(item.captured_at))
        ),
        hashesMatch: hashes.every(Boolean),
        loaded: images.every(image => image.complete && image.naturalWidth > 0),
        captioned: numbered.every(image =>
          image.closest(".recorded-capture")?.querySelector(".capture-note")?.textContent ===
          (english ? "Actual Korean-run frame · numbered guidance added" : "실제 한국어 실행 녹화 · 번호는 안내 주석")),
      };
    }, {english, edition, stepManifest: page.contosoGuideRelease.portal_step_manifest});
    check(captures.declared.length === edition.portal_screenshots && captures.rendered.length === 0
      && await page.locator(".historical-screen").count() === 0,
    "historical captures remain preserved without old-screen references in the learner guide");
    check(captures.genuine && captures.scoped && captures.provenance && captures.hashesMatch, "preserved portal captures and current frames retain genuine scoped provenance and original hashes");
    check(captures.loaded && captures.captioned, "all offline portal images load with concise screen-example captions");
    check(captures.deferred, "portal screenshots load lazily and reserve their size, so the first page does not download every image");
    check(captures.framesDeclared.length > 0
      && JSON.stringify(captures.framesDeclared) === JSON.stringify(captures.framesRendered),
    "every reviewed numbered screen appears in this language edition");
    check(captures.reviewedFrames && captures.nativeSizes, "numbered screens keep reviewed source-video hashes and native crop dimensions");
    check(JSON.stringify(captures.visualModules.map(module => module.id)) === JSON.stringify(labIds)
      && captures.visualModules.every(module => module.complete && (terminalIds.includes(module.id)
        ? module.diagrams.includes(diagrams[module.id]) && module.sourceBlocks > 0 && module.commandBlocks > 0
        : module.cards >= 2)),
    "portal modules use exact numbered scenes; code-required modules use loaded flow diagrams, source, and commands");
    check(captures.visualModules.filter(module => ["l15", "l15-collaboration"].includes(module.id))
      .every(module => module.cards === 0),
    "MAF workflows are not illustrated with unrelated Prompt Agent screenshots");
    await page.goto(`${entry}#l04`);
    const fullSize = page.locator("#l04 a.screen-image").first();
    await fullSize.focus();
    check(await fullSize.evaluate(node => node === document.activeElement), "full-size screen links are keyboard focusable");
    const [enlarged] = await Promise.all([page.waitForEvent("popup"), fullSize.press("Enter")]);
    try {
      await enlarged.waitForLoadState("load");
      check(enlarged.url() === new URL(await fullSize.getAttribute("href"), entry).href
        && await enlarged.locator("img").evaluate(image => image.complete && image.naturalWidth > 0),
      "Enter opens the original full-size local image");
    } finally {
      await enlarged.close();
    }
    for (const id of terminalIds) {
      await page.goto(`${entry}#${id}`);
      const diagram = page.locator(`#${id} a`).filter({has: page.locator(`img[src="${diagrams[id]}"]`)});
      await diagram.focus();
      check(await diagram.evaluate(node => node === document.activeElement),
        `${id} full-size flow diagram is keyboard accessible`);
      const address = new URL(diagrams[id], entry).href;
      await Promise.all([page.waitForURL(address), diagram.press("Enter")]);
      check(await page.locator("svg").isVisible(), `${id} opens its genuine local SVG at full size`);
    }
    await page.goto(`${entry}#l00`);
    check(await page.locator('.provenance-note, a[href^="content/portal-screenshots"]').count() === 0,
      "capture audits stay in maintenance records rather than learner navigation");
    check(await page.locator('a[href^="validation/"], a[href^="results/"]').count() === 0, "execution records remain outside the guide");
    for (const path of [edition.receipt_html]) {
      check(await page.locator(`.site-footer a[href="${path}"]`).count() === 1, `footer uses localized link: ${path}`);
      const response = await page.request.get(`${origin}/${path}`);
      check(response.ok(), `localized receipt/evidence file is available: ${path}`);
      if (path === edition.receipt_html) {
        check((await response.text()).includes(`<html lang="${edition.language}">`), "synthetic receipt matches the reader language");
      }
    }
    for (const path of [edition.readme, edition.markdown, page.contosoGuideRelease.archive,
      page.contosoGuideRelease.portal_inputs, page.contosoGuideRelease.portal_recordings]) {
      const response = await page.request.get(`${origin}/${path}`);
      check(response.ok(), `download is available: ${path}`);
    }
    for (const source of ["samples/workshop.py", "azure.yaml", ".env.example", ".github/workflows/validate.yml"]) {
      const response = await page.request.get(`${origin}/${source}`);
      check(response.ok() && response.headers()["content-type"].startsWith("text/plain"), `source is readable as text: ${source}`);
    }
    check(await page.locator(".chapter.active").getAttribute("id") === "l00", "home route");
    check(await page.locator("html").getAttribute("lang") === edition.language, "correct language metadata");
    check(await page.locator(".brand-product").innerText() === "Microsoft Foundry",
      "the reader header uses the full Microsoft Foundry product name");
    check(await page.locator(".topbar .edition").innerText() ===
      (english ? "Contoso Purchasing Agent" : "Contoso 구매 에이전트"),
      "topbar shows the localized agent name without the edition date");
    check(await page.locator("#print-one, #print-all").count() === 0, "reader omits print controls");
    check(await page.locator("a[href]").evaluateAll(nodes =>
      nodes.every(node => !new URL(node.href).pathname.toLowerCase().endsWith(".pdf"))
    ), "reader omits PDF downloads");
    check(await page.locator('script[src^="http"],link[rel="stylesheet"][href^="http"]').count() === 0, "no remote runtime dependencies");
    check(await page.locator('.language-switch a[aria-current="true"]').getAttribute("lang") === edition.language, "current language is accessible");
    const rootResponse = await page.request.get(`${origin}/`);
    check((await rootResponse.text()).includes('<html lang="en">'), "site root defaults to English");
    const bodyText = await page.locator("body").textContent();
    check(bodyText.includes("Contoso") && !bodyText.includes("한빛") && !bodyText.includes("Hanbit"), "current scenario is consistently Contoso");
    check(!/Playwright MCP|Headless Chromium|가이드 밖|outside (?:the|this) guide/.test(bodyText),
      "learner text omits authoring tools and audit-storage instructions");
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

    check(await page.locator(".hero .primary-link").getAttribute("href") === "#l00-first-steps", "the primary start action opens concepts, not provisioning");
    await page.locator(".hero .primary-link").click();
    await page.waitForFunction(() => document.activeElement.id === "l00-first-steps");
    check(await page.locator(".chapter.active").getAttribute("id") === "l00", "first-time readers stay in L00");
    check(await page.evaluate(() => document.activeElement.id) === "l00-first-steps", "first-step navigation moves keyboard focus");
    check(await page.locator(`.hero a[href="${page.contosoGuideRelease.archive}"]`).count() === 1, "lab ZIP is available at the entry point");
    check(await page.locator('.hero a[href="#l01"]').innerText().then(text => /portal|포털/.test(text)),
      "the entry point identifies portal setup as the default path");
    const environmentOptions = page.locator(".hero .environment-options");
    check(await environmentOptions.evaluate(node => !node.open)
      && await environmentOptions.locator('a[href="downloads/Contoso-Portal-Inputs.zip"]').isHidden(),
      "input files and videos remain available in the collapsed download choices");
    await environmentOptions.locator("summary").click();
    check(await environmentOptions.locator(`a[href="${page.contosoGuideRelease.archive}"]`).isVisible(),
      "offline files remain available when the alternative is expanded");
    check(await environmentOptions.locator('a[href="downloads/portal/index.html"]').isVisible(),
      "actual portal recordings are linked separately from reconstructed replays");
    await environmentOptions.locator("summary").click();
    await page.goto(`${entry}#l01`);
    check(await page.locator("#l01 pre, #l01 .setup-detail, #l01 .pc-setup").count() === 0,
      "portal provisioning does not hide a second local-installation path");
    for (const id of ["l01-pc", "l01-codespaces", "l01-python", "l01-azure-cli",
      "l01-vscode", "l01-interpreter", "l01-new-terminal"]) {
      await page.goto(`${entry}#${id}`);
      await page.waitForFunction(id => document.activeElement.id === id, id);
      check(await page.locator(".chapter.active").getAttribute("id") === "l01",
        `compatibility bookmark ${id} returns to portal resumption`);
    }
    await page.goto(`${entry}#l01-sign-in`);
    await page.waitForFunction(() => document.activeElement.id === "l01-sign-in");
    check(await page.locator('#l01 a[href="https://portal.azure.com/"]').count() > 0
      && await page.locator('#l01 a[href="https://ai.azure.com/"]').count() > 0,
      "authentication uses the two named portals without opening external links during local validation");
    await page.goto(`${entry}#l07`);
    check(await page.locator("#l07").innerText().then(text =>
      text.includes("https://learn.microsoft.com/api/mcp") && !text.includes("python samples/inventory_api.py")
    ), "MCP practice names a real remote read-only tool rather than requiring a local server");
    await page.goto(`${entry}#l12-codespaces`);
    await page.waitForFunction(() => document.activeElement.id === "l12-codespaces");
    check(await page.locator(".chapter.active").getAttribute("id") === "l12",
      "old environment-stop bookmarks resolve within shared cost/retention wrap-up");
    await page.goto(`${entry}#l08`);
    check(await page.locator("#l08 .recorded-answer").count() === 0, "author execution answers are not embedded in the guide");
    check(await page.locator("#l08 pre").count() === 0, "evaluation uses file upload and field mapping, not copied CLI collection");
    const dataPrefix = english ? "data/en" : "data";
    for (const version of ["v1", "v2"]) {
      check(await page.locator(`#l08 a[href="${dataPrefix}/prompts/agent-${version}.txt"]`).count() === 1,
        `L08 exposes the localized ${version} instruction source`);
    }
    check(await page.locator("#l08").innerText().then(text => text.includes("compound-request-no-tools")),
      "the default reading path identifies the fixed question without inventing a score");

    await page.goto(`${entry}#l03`);
    check(await page.locator("#l03 pre code.language-prompt").isVisible()
      && await page.locator("#l03 .implementation-detail").count() === 0,
      "the first response is a visible portal question without an SDK execution detour");
    await page.goto(`${entry}#l08`);
    check(await page.locator("#l08").innerText().then(text =>
      ["evaluation-12.jsonl", "{{item.query}}", "ground_truth", "Partial/Failed", "12"].every(term => text.includes(term))
    ), "evaluation maps questions separately from judge-only context and preserves failed rows");
    await page.goto(`${entry}#l11`);
    await page.locator("#l06.active").waitFor({state: "visible"});
    check(await page.locator(".chapter.active").getAttribute("id") === "l06", "old capstone bookmarks open the integrated L06 review");
    check(await page.locator("#l06").innerText().then(text =>
      text.includes("draft_requires_human_approval") && text.includes("order_submitted=false")
      && !text.includes("capstone --live")
    ), "integrated review retains the draft contract without claiming a backend execution");

    await page.goto(`${entry}#l07`);
    const portalHeading = await page.locator("#l07 .prose h2[id]").first().getAttribute("id");
    await page.goto(`${entry}#${encodeURIComponent(portalHeading)}`);
    await page.waitForFunction(id => document.activeElement.id === id, portalHeading);
    check(await page.locator(".chapter.active").getAttribute("id") === "l07", "deep-linked portal headings select their containing module");
    check(await page.evaluate(() => document.activeElement.id) === portalHeading, "deep-linked portal heading receives keyboard focus");

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
    await page.locator("#l00.active").waitFor({state: "visible"});
    const quick = await page.locator(".chapter-link:visible").evaluateAll(nodes => nodes.map(node => node.dataset.chapter));
    check(quick.join(",") === "l00,l01,l04,l05,l08,l12,instructor", "90-minute path matches the instructor schedule");
    await page.locator('.chapter-link[data-chapter="l01"]').click();
    await page.locator("#l01.active").waitFor({state: "visible"});
    for (const next of ["l04", "l05", "l08", "l12"]) {
      check(await page.locator(".chapter.active .chapter-pagination .next").getAttribute("href") === `#${next}`, `90-minute next action follows ${next}`);
      await page.locator(".chapter.active .chapter-pagination .next").click();
      await page.locator(`#${next}.active`).waitFor({state: "visible"});
      check(await page.locator("#learning-path").inputValue() === "quick", "next navigation preserves the selected learning path");
    }
    await page.locator("#learning-path").selectOption("core");
    check(await page.locator("#l12 .chapter-pagination .next").getAttribute("href") === "#l00", "core completion does not require advanced electives");
    await page.goto(`${entry}#l10`);
    check(await page.locator("#l10 .chapter-pagination .next").getAttribute("href") === "#l12", "core-only readers go directly from L10 to L19 wrap-up");
    check(await page.locator('.chapter-link[data-chapter="l12"] .nav-number').innerText() === "19", "the old cleanup bookmark displays L19");
    await page.locator("#learning-path").selectOption("all");
    await page.locator('.chapter-link[data-chapter="l06"]').click();
    await page.locator('[data-complete="l06"]').click();
    check(await page.locator("#progress-label").innerText() === `1 / ${labIds.length}`, "progress increments");
    await page.locator("#learning-path").selectOption("core");
    check(await page.locator("#progress-label").innerText() === `1 / ${corePathCount}`, "core progress counts only core modules and wrap-up");
    check(await page.locator("#progress").getAttribute("max") === String(corePathCount), "progress meter matches its visible denominator");
    await page.locator('.reader-help a[href="#glossary"]').click();
    await page.locator("#glossary.active").waitFor({state: "visible"});
    check(await page.locator("#learning-path").inputValue() === "core", "opening glossary does not reset the learning path");
    check(await page.locator("#glossary .return-to-lab").getAttribute("href") === "#l06", "help remembers the originating lab");
    check(await page.locator("#glossary .chapter-pagination .next").getAttribute("href") === "#l06", "help footer returns to the originating lab too");
    await page.locator("#glossary .return-to-lab").click();
    await page.locator("#l06.active").waitFor({state: "visible"});
    await page.locator('.reader-help a[href="#troubleshooting"]').click();
    await page.locator("#troubleshooting.active").waitFor({state: "visible"});
    check(await page.locator("#learning-path").inputValue() === "core", "troubleshooting preserves the selected path");
    await page.locator("#troubleshooting .return-to-lab").click();
    await page.locator("#l06.active").waitFor({state: "visible"});
    await page.goto(`${entry}#l06-failures`);
    await page.waitForFunction(() => document.activeElement.id === "l06-failures");
    await page.evaluate(() => window.scrollBy(0, 160));
    const readingPosition = await page.evaluate(() => window.scrollY);
    await page.locator('.reader-help a[href="#glossary"]').click();
    await page.locator("#glossary.active").waitFor({state: "visible"});
    check(await page.locator("#glossary .return-to-lab").getAttribute("href") === "#l06-failures",
      "help retains the exact lab section, not just the module");
    await page.locator('.reader-help a[href="#troubleshooting"]').click();
    await page.locator("#troubleshooting.active").waitFor({state: "visible"});
    check(await page.locator("#troubleshooting .chapter-pagination .next").getAttribute("href") === "#l06-failures",
      "moving between references preserves the original lab section");
    await page.locator("#troubleshooting .chapter-pagination .next").click();
    await page.waitForFunction(() => document.activeElement.id === "l06-failures");
    check(Math.abs(await page.evaluate(() => window.scrollY) - readingPosition) <= 1,
      "returning from help restores the exact reading position");
    check(await page.locator("#learning-path").inputValue() === "core", "section-level help return preserves the core path");
    await page.locator("#learning-path").selectOption("quick");
    await page.locator("#l00.active").waitFor({state: "visible"});
    check(await page.locator("#progress-label").innerText() === "0 / 6", "quick tour excludes completed labs outside its six modules");
    await page.locator("#learning-path").selectOption("advanced");
    await page.locator("#l13.active").waitFor({state: "visible"});
    check(await page.locator("#progress-label").innerText() === `0 / ${advancedPathCount}`, "elective progress includes shared wrap-up but not core labs");
    check(JSON.stringify(await page.locator(".chapter-link:visible .nav-number").allTextContents()) === JSON.stringify(expectedNumbers.slice(11)),
      "advanced navigation is continuous from L11 to L18 and then L19 wrap-up");
    await page.goto(`${entry}#l22`);
    check(await page.locator("#l22 .chapter-pagination .next").getAttribute("href") === "#l12", "the final elective leads to shared wrap-up");
    await page.goto(`${entry}#l12`);
    check(await page.locator("#l12 .chapter-pagination .next").getAttribute("href") === "#l00", "advanced completion ends after wrap-up");
    await page.locator('[data-complete="l12"]').click();
    await page.locator("#learning-path").selectOption("core");
    check(await page.locator("#progress-label").innerText() === `2 / ${corePathCount}`, "wrap-up completion is shared with the core path");
    await page.locator('[data-complete="l12"]').click();
    await page.locator("#learning-path").selectOption("advanced");
    await page.goto(`${entry}#l17`);
    check(await page.locator("#l17 .chapter-pagination .next").getAttribute("href") === "#l21", "elective pagination follows displayed L16 to L17 despite stable internal IDs");
    await page.locator("#l17 .chapter-pagination .next").click();
    await page.locator("#l21.active").waitFor({state: "visible"});
    check(await page.locator("#l21 .chapter-pagination a").first().getAttribute("href") === "#l17", "reverse pagination follows continuous displayed numbers");
    await page.locator("#learning-path").selectOption("offline");
    await page.locator("#l21.active").waitFor({state: "visible"});
    check(await page.locator(".chapter.active").getAttribute("id") === "l21", "path switching retains a current lab that belongs to both paths");
    check(await page.locator("#path-scope").isVisible(), "without-Azure scope warning persists beyond a transient toast");
    check(await page.locator(".chapter-link:visible").count() === chapters.length,
      "the read-only path includes all modules without claiming Azure execution");
    await page.locator("#learning-path").selectOption("reference");
    await page.locator("#troubleshooting.active").waitFor({state: "visible"});
    check(await page.locator(".progress-card").isHidden(), "reference material does not display a misleading completion target");
    await page.locator("#learning-path").selectOption("all");
    await page.goto(`${entry}#l06`);
    check(await page.locator("#progress-label").innerText() === `1 / ${labIds.length}`, "path switches preserve all existing completion records");
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
    check(await page.locator("#l06 .code-label").first().innerText().then(text =>
      text.includes("Chat") && !/Bash|Terminal|터미널/.test(text)),
      "input labels identify portal Chat rather than a shell");
    await page.locator("#l06 .copy-button").first().click();
    check(await page.evaluate(() => window.__workshopCopiedText) === expectedCode, "copy includes code only, not labels");
    await page.goto(`${entry}#l01`);
    check(await page.locator("#l01 .copy-button").count() === 0,
      "resource creation cannot be mistaken for an environment-file or terminal copy action");
    await page.goto(`${entry}#l03`);
    const firstQuestion = page.locator("#l03 pre").filter({has: page.locator("code.language-prompt")}).first();
    await firstQuestion.locator(".copy-button").click();
    check(await page.evaluate(() => window.__workshopCopiedText) === await firstQuestion.locator("code").textContent(),
      "copying a question preserves its exact text without sending a paid request");
    await page.goto(`${entry}#l04`);
    const question = page.locator("#l04 pre").filter({has: page.locator("code.language-prompt")}).first();
    await question.locator(".copy-button").click();
    check((await page.locator("#toast").innerText()).includes("Chat"), "question copy directs the learner to portal Chat");
    for (const [id, kind, destination] of [
      ["l14", "bash", english ? "Terminal" : "터미널"],
      ["l14", "powershell", "PowerShell"],
      ["l14", "yaml", english ? "Configuration" : "설정"],
      ["l14", "env", ".env"],
      ["l15", "python", english ? "Python excerpt" : "Python"],
      ["l15", "output", english ? "Example output" : "예시"],
    ]) {
      await page.goto(`${entry}#${id}`);
      const block = page.locator(`#${id} pre`).filter({has: page.locator(`code.language-${kind}`)}).first();
      const expected = await block.locator("code").textContent();
      await block.locator(".copy-button").click();
      check(await page.evaluate(() => window.__workshopCopiedText) === expected,
        `${id} ${kind} copy preserves exact source without executing it`);
      check((await page.locator("#toast").innerText()).includes(destination)
        && !(await page.locator("#toast").innerText()).includes("Chat"),
      `${id} ${kind} copy identifies its actual destination, not portal Chat`);
    }
    await page.goto(`${entry}#l06`);
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
      if (width <= 390) {
        await page.goto(`${entry}#l00`);
        const options = page.locator(".hero .environment-options");
        if (!await options.evaluate(node => node.open)) await options.locator("summary").click();
        check(await options.locator("a").evaluateAll(nodes => nodes.every(node => {
          const box = node.getBoundingClientRect();
          const hero = node.closest(".hero").getBoundingClientRect();
          return box.width > 0 && box.left >= hero.left && box.right <= hero.right
            && node.scrollWidth <= node.clientWidth + 1;
        })), `expanded environment links remain usable at ${width}px`);
        await options.locator("summary").click();
      }
      await page.goto(`${entry}#l08`);
      const measure = await page.evaluate(() => ({
        viewport: innerWidth,
        document: document.documentElement.scrollWidth,
        prose: parseFloat(getComputedStyle(document.querySelector(".chapter.active .prose")).fontSize),
        code: parseFloat(getComputedStyle(document.querySelector(".chapter.active code")).fontSize),
        navigation: parseFloat(getComputedStyle(document.querySelector(".chapter-link")).fontSize),
        table: parseFloat(getComputedStyle(document.querySelector(".chapter.active td")).fontSize),
        brandRight: document.querySelector(".brand").getBoundingClientRect().right,
        actionsLeft: document.querySelector(".top-actions").getBoundingClientRect().left,
      }));
      check(measure.document <= measure.viewport + 1, `no document overflow at ${width}px`);
      check(measure.prose >= 16, `body text >= 16px at ${width}px`);
      check(measure.code >= 14, `code text >= 14px at ${width}px`);
      check(measure.navigation >= 14, `navigation text >= 14px at ${width}px`);
      check(measure.table >= 14, `table text >= 14px at ${width}px`);
      check(measure.brandRight <= measure.actionsLeft, `brand and header controls do not overlap at ${width}px`);
      check(await page.locator(`.language-switch [data-language="${other}"]`).isVisible(), `language switch remains available at ${width}px`);
      await page.goto(`${entry}#l04`);
      const imageBounds = await page.locator("#l04 .portal-capture img").evaluateAll(async images => {
        await Promise.all(images.map(image => { image.loading = "eager"; return image.decode().catch(() => {}); }));
        return images.map(image => ({
          width: image.getBoundingClientRect().width,
          container: image.closest("figure").getBoundingClientRect().width,
          loaded: image.complete && image.naturalWidth > 0,
        }));
      });
      check(imageBounds.length > 0 && imageBounds.every(image => image.loaded && image.width <= image.container + 1), `portal screenshots fit the reader at ${width}px`);
      if ([1440, 390, 320].includes(width)) {
        for (const id of labIds) {
          await page.goto(`${entry}#${id}`);
          const expandableSetup = page.locator(
            `#${id} :is(.implementation-detail, .environment-option, .resume-setup, .setup-detail)`
          );
          const expandedStates = await expandableSetup.evaluateAll(nodes => {
            const states = nodes.map(node => node.open);
            nodes.forEach(node => { node.open = true; });
            return states;
          });
          const layout = await page.locator(`#${id}.active`).evaluate(chapter => ({
            viewport: innerWidth,
            document: document.documentElement.scrollWidth,
            tables: chapter.querySelectorAll(".table-wrap table").length,
            briefWidth: chapter.querySelector(".lab-brief").getBoundingClientRect().width,
            handoffWidth: chapter.querySelector(".lab-handoff").getBoundingClientRect().width,
            proseWidth: chapter.querySelector(".prose").getBoundingClientRect().width,
            walkthroughsFit: [...chapter.querySelectorAll(".table-wrap")].every(node =>
              node.getBoundingClientRect().width <= chapter.querySelector(".prose").getBoundingClientRect().width + 1
            ),
            imagesFit: [...chapter.querySelectorAll(".prose img")].every(image =>
              image.getBoundingClientRect().width <= chapter.querySelector(".prose").getBoundingClientRect().width + 1
            ),
            labelsFit: [...chapter.querySelectorAll(".code-label")].every(label => {
              if (!label.getClientRects().length) return true;
              const pre = label.closest("pre");
              const button = pre.querySelector(".copy-button");
              const code = pre.querySelector("code");
              return label.getBoundingClientRect().right <= button.getBoundingClientRect().left &&
                label.getBoundingClientRect().bottom <= code.getBoundingClientRect().top;
            }),
          }));
          check(layout.document <= layout.viewport + 1 && layout.tables > 0, `${id} decision tables fit the reader at ${width}px`);
          check(layout.briefWidth > 0 && layout.briefWidth <= layout.proseWidth + 1, `${id} beginner card fits at ${width}px`);
          check(layout.handoffWidth > 0 && layout.handoffWidth <= layout.proseWidth + 1, `${id} result handoff fits at ${width}px`);
          check(layout.walkthroughsFit, `${id} portal action tables stay within the reading surface at ${width}px`);
          check(layout.imagesFit, `${id} screenshots and flow diagrams fit the reading surface at ${width}px`);
          check(layout.labelsFit, `${id} input labels do not overlap copy controls or code at ${width}px`);
          if (practiceIds.includes(id)) {
            check(await page.locator(`#${id} .practice-block`).isVisible(), `${id} concrete practice remains readable at ${width}px`);
          }
          await expandableSetup.evaluateAll((nodes, states) => {
            nodes.forEach((node, index) => { node.open = states[index]; });
          }, expandedStates);
        }
      }
    }
    await page.setViewportSize({width: 390, height: 844});
    await page.goto(`${entry}#l06-failures`);
    await page.waitForFunction(() => document.activeElement.id === "l06-failures");
    await page.evaluate(() => window.scrollBy(0, 80));
    const mobileReadingPosition = await page.evaluate(() => window.scrollY);
    const menuBounds = await page.locator("#menu-toggle").boundingBox();
    check(menuBounds !== null, "mobile contents control is visible");
    // Locator auto-scroll can move the page before clicking this sticky control.
    await page.mouse.click(menuBounds.x + menuBounds.width / 2, menuBounds.y + menuBounds.height / 2);
    check(Math.abs(await page.evaluate(() => window.scrollY) - mobileReadingPosition) <= 1,
      "opening the mobile contents does not move the underlying reading position");
    await page.locator('.reader-help a[href="#troubleshooting"]').click();
    await page.locator("#troubleshooting.active").waitFor({state: "visible"});
    await page.locator("#troubleshooting .return-to-lab").click();
    await page.waitForFunction(() => document.activeElement.id === "l06-failures");
    check(Math.abs(await page.evaluate(() => window.scrollY) - mobileReadingPosition) <= 1,
      "mobile help returns to the original reading position and section");
    check(await page.locator("#menu-toggle").getAttribute("aria-expanded") === "false",
      "mobile help return leaves the contents menu closed");
    await page.locator("#menu-toggle").click();
    check(await page.locator("#menu-toggle").getAttribute("aria-expanded") === "true", "mobile menu opens");
    await page.locator('.chapter-link[data-chapter="l21"]').click();
    await page.locator("#l21.active").waitFor({state: "visible"});
    check(await page.locator(".chapter.active").getAttribute("id") === "l21", "mobile navigation");
    check(await page.locator("#menu-toggle").getAttribute("aria-expanded") === "false", "mobile menu closes after navigation");
    await page.locator(".brand").click();
    await page.locator("#l00.active").waitFor({state: "visible"});
    check(await page.locator(".chapter.active").getAttribute("id") === "l00", "official brand icon still links to the start");

    await page.setViewportSize({width: 1440, height: 1000});
    for (const id of labIds) {
      await page.goto(`${entry}#${id}`);
      await page.locator(`#${id}.active`).waitFor({state: "visible"});
      check(await page.locator(".chapter.active").getAttribute("id") === id, `direct route ${id}`);
    }
    await page.goto(`${entry}#coverage`);
    check(await page.locator("#coverage tbody tr").count() === 72, "68 coverage rows plus 4 depth definitions");
    await page.goto(`${entry}#%E0%A4%A`);
    check(await page.locator(".chapter.active").getAttribute("id") === "l00", "malformed hash has a safe fallback");

    await page.goto(`${origin}/${page.contosoGuideRelease.portal_recordings}`);
    check(await page.locator("#portal-coverage tbody tr").count() === labIds.length,
      "actual recordings disclose coverage and non-execution for every module");
    const recordings = await page.evaluate(async () => {
      const response = await fetch("../../content/portal-recordings.json");
      if (!response.ok) throw new Error("Missing actual recording provenance.");
      return response.json();
    });
    const verifyRecordings = async (mediaPage, surface) => {
      check(recordings.clips.length > 0 && await mediaPage.locator("video").count() === recordings.clips.length,
        `${surface}: all declared actual portal recordings are available separately from replays`);
      for (const [index, clip] of recordings.clips.entries()) {
        const recording = mediaPage.locator("video").nth(index);
        check(await recording.locator("source").getAttribute("src") === `${clip.id}.mp4`,
          `${surface}: ${clip.id} uses its declared local media`);
        await recording.evaluate(video => {
          video.muted = true;
          video.preload = "metadata";
          video.load();
          [...video.textTracks].forEach(track => { track.mode = "hidden"; });
        });
        await mediaPage.waitForFunction(index => {
          const video = document.querySelectorAll("video")[index];
          return video.readyState >= 1 && (location.protocol === "file:"
            || [...video.querySelectorAll("track")].every(track => track.readyState === 2));
        }, index);
        check(await recording.evaluate((video, clip) =>
          Number.isFinite(video.duration) && Math.abs(video.duration - clip.seconds) < .15
          && video.textTracks.length === 2
          && [...video.textTracks].map(track => track.language).sort().join(",") === "en,ko"
          && [...video.textTracks].every(track => track.cues.length === clip.edits.length
            && [...track.cues].every((cue, index) =>
              cue.text === clip.edits[index].caption[track.language]
              && Math.abs(cue.startTime - clip.edits[index].start_seconds) < .001
              && Math.abs(cue.endTime - clip.edits[index].end_seconds) < .001)), clip),
        `${surface}: ${clip.id} decodes with matching duration and complete Korean/English captions`);
        await recording.evaluate(video => video.play());
        await mediaPage.waitForFunction(index => document.querySelectorAll("video")[index].currentTime > .1, index);
        await recording.evaluate(video => video.pause());
      }
    };
    await verifyRecordings(page, "HTTP");
    if (english) {
      const verifySceneLinks = async (mediaPage, base, surface) => {
        check(captures.timedFrames.length === 3, `${surface}: scene tests include both fractional inspection frames`);
        const waitForScene = async (clip, seconds, language) => {
          await mediaPage.waitForFunction(({clip, seconds, language}) => {
            const video = [...document.querySelectorAll("video")].find(item => item.dataset.recording === clip);
            return document.getElementById("recording-link-status").dataset.state === "ready"
              && video.readyState >= 2 && !video.seeking && Math.abs(video.currentTime - seconds) < .15
              && [...video.textTracks].some(track =>
                track.language === language && track.mode === "showing" && track.cues?.length > 0);
          }, {clip, seconds, language}, {timeout: 15000});
        };
        const clip = recordings.clips[0];
        const sceneIndex = clip.edits.findIndex(edit => edit.start_seconds > 0);
        check(sceneIndex >= 0, `${surface}: an actual nonzero scene is available for link-click regression`);
        for (const language of ["ko", "en"]) {
          await mediaPage.goto(base);
          const scenes = mediaPage.locator(`[id="${clip.id}"] details`);
          await scenes.locator("summary").click();
          const link = scenes.locator(`a[lang="${language}"]`).nth(sceneIndex);
          const address = new URL(await link.getAttribute("href"), base);
          const seconds = clip.edits[sceneIndex].start_seconds;
          check(address.pathname === new URL(base).pathname && address.searchParams.get("clip") === clip.id
            && Number(address.searchParams.get("t")) === seconds && address.searchParams.get("lang") === language,
          `${surface}: ${language} scene links open the captioned player, not a bare MP4`);
          await Promise.all([mediaPage.waitForURL(address.href), link.click()]);
          await waitForScene(clip.id, seconds, language);
          check(await mediaPage.locator("video").evaluateAll((videos, clip) => videos.every(video =>
            video.paused && !video.autoplay && (video.dataset.recording === clip || video.readyState === 0)
          ), clip.id), `${surface}: clicking a ${language} scene selects captions and time without autoplay or other clips`);
        }
        for (const frame of captures.timedFrames) {
          for (const language of ["ko", "en"]) {
            const address = new URL(base);
            address.search = new URLSearchParams({clip: frame.clip, t: frame.seconds, lang: language}).toString();
            address.hash = frame.clip;
            await mediaPage.goto(address.href);
            await waitForScene(frame.clip, frame.seconds, language);
            check(await mediaPage.locator("video").evaluateAll((videos, clip) =>
              videos.every(video => video.paused && !video.autoplay && video.playbackRate === 1
                && (video.dataset.recording === clip || video.readyState === 0))
              && [...videos.find(video => video.dataset.recording === clip).textTracks]
                .filter(track => track.mode === "showing").length === 1, frame.clip),
            `${surface}: ${frame.clip} seeks to ${frame.seconds}s with ${language} captions, without autoplay or loading other clips`);
          }
        }
        for (const query of [
          `clip=missing&t=0&lang=en`, `clip=${clip.id}&t=-1&lang=en`,
          `clip=${clip.id}&t=NaN&lang=en`, `clip=${clip.id}&t=${clip.seconds}&lang=en`,
          `clip=${clip.id}&t=&lang=en`, `clip=${clip.id}&t=0&lang=fr`,
          `clip=${clip.id}&t=0`, `clip=${clip.id}&t=0&lang=en&t=1`,
        ]) {
          await mediaPage.goto(`${base}?${query}`);
          check(await mediaPage.locator("#recording-link-status").getAttribute("data-state") === "error"
            && await mediaPage.locator("#recording-link-status").isVisible()
            && await mediaPage.locator("video").evaluateAll(videos => videos.every(video => video.readyState === 0 && video.paused)),
          `${surface}: invalid scene link reports an explicit warning without loading media: ${query}`);
        }
      };
      await verifySceneLinks(page, `${origin}/${page.contosoGuideRelease.portal_recordings}`, "HTTP");
      const offlineContext = await page.context().browser().newContext();
      const offline = await offlineContext.newPage();
      offline.setDefaultTimeout(30000);
      offline.on("pageerror", onError);
      offline.on("console", message => { if (message.type() === "error") errors.push(message.text()); });
      await offline.route("**/*", async route => {
        if (new URL(route.request().url()).protocol !== "file:") {
          remoteRequests.push(route.request().url());
          await route.abort("blockedbyclient");
        } else {
          await route.continue();
        }
      });
      try {
        await offline.goto(page.contosoGuideRecordingFile);
        await verifyRecordings(offline, "Offline file");
        await verifySceneLinks(offline, page.contosoGuideRecordingFile, "Offline file");
      } finally {
        await offlineContext.close();
      }
    }

    const context = await page.context().browser().newContext({javaScriptEnabled: false});
    try {
      await context.route("**/*", localOnly);
      const nojs = await context.newPage();
      await nojs.goto(entry);
      check(await nojs.locator(".chapter:visible").count() === chapters.length, "all content readable without JavaScript");
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
