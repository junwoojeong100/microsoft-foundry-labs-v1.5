async (page) => {
  const base = page.contosoGuideOrigin || "http://127.0.0.1:8765";
  await page.goto(`${base}/index.html#l00`);
  await page.reload();
  await page.waitForLoadState("networkidle");
  await page.evaluate(() => {
    document.title = "Contoso Microsoft Foundry 실습 가이드 | 2026-09-30";
    document.body.dataset.print = "all";
    window.dispatchEvent(new Event("beforeprint"));
  });
  await page.emulateMedia({media: "print"});
  if (await page.locator(".chapter:visible").count() !== 30) {
    throw new Error("All 30 guide sections must be visible before PDF export.");
  }
  if (await page.locator('a[href^="assets/"], a[href^="validation/"]').count() !== 0) {
    throw new Error("Local file links must become plain references in a portable PDF.");
  }
  if (await page.locator(".print-toc a").first().getAttribute("href") !== "#l00-title") {
    throw new Error("PDF table of contents must target visible module headings.");
  }
  try {
    const output = await page.pdf({
      path: "Contoso-Foundry-Hands-on-2026-09-30.pdf",
      format: "A4",
      preferCSSPageSize: true,
      printBackground: true,
      displayHeaderFooter: true,
      tagged: true,
      outline: true,
      headerTemplate: '<div style="width:100%;font-family:Arial;font-size:8px;color:#536976;padding:0 13mm;">MICROSOFT FOUNDRY · HANDS-ON GUIDE</div>',
      footerTemplate: '<div style="width:100%;font-family:Arial;font-size:8px;color:#536976;display:flex;justify-content:space-between;padding:0 13mm;"><span>2026-09-30 · Contoso independent edition</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>',
    });
    return {pdf: "Contoso-Foundry-Hands-on-2026-09-30.pdf", bytes: output.length};
  } finally {
    await page.evaluate(() => window.dispatchEvent(new Event("afterprint")));
    await page.emulateMedia({media: null});
    await page.reload();
  }
}
