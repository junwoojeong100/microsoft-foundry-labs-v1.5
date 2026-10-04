async (page) => {
  const base = page.contosoGuideOrigin || "http://127.0.0.1:8765";
  const edition = page.contosoGuideEdition;
  await page.goto(`${base}/${edition.html}#l00`);
  await page.reload();
  await page.waitForLoadState("networkidle");
  await page.evaluate(edition => {
    document.title = `Contoso Microsoft Foundry | ${edition.label} | ${edition.date}`;
    document.body.dataset.print = "all";
    window.dispatchEvent(new Event("beforeprint"));
  }, edition);
  await page.emulateMedia({media: "print"});
  const chapterCount = await page.locator(".chapter").count();
  if (chapterCount === 0 || await page.locator(".chapter:visible").count() !== chapterCount) {
    throw new Error(`All ${chapterCount} guide sections must be visible before PDF export.`);
  }
  if (await page.locator('a[href^="assets/"], a[href^="validation/"]').count() !== 0) {
    throw new Error("Local file links must become plain references in a portable PDF.");
  }
  if (await page.locator(".print-toc a").first().getAttribute("href") !== "#l00-title") {
    throw new Error("PDF table of contents must target visible module headings.");
  }
  try {
    const output = await page.pdf({
      path: edition.pdf,
      format: "A4",
      preferCSSPageSize: true,
      printBackground: true,
      displayHeaderFooter: true,
      tagged: true,
      outline: true,
      headerTemplate: '<div style="width:100%;font-family:Arial;font-size:8px;color:#536976;padding:0 13mm;">MICROSOFT FOUNDRY · HANDS-ON GUIDE</div>',
      footerTemplate: `<div style="width:100%;font-family:Arial;font-size:8px;color:#536976;display:flex;justify-content:space-between;padding:0 13mm;"><span>${edition.date} · Contoso · ${edition.language}</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>`,
    });
    return {pdf: edition.pdf, language: edition.language, bytes: output.length};
  } finally {
    await page.evaluate(() => window.dispatchEvent(new Event("afterprint")));
    await page.emulateMedia({media: null});
    await page.reload();
  }
}
