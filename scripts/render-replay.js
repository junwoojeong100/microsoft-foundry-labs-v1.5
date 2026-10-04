"use strict";

const fs = require("node:fs/promises");
const path = require("node:path");
const { chromium } = require("playwright");
const root = path.resolve(__dirname, "..");
const escape = value => String(value).replace(/[&<>"']/g, c => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
}[c]));

async function main() {
  const [language, output] = process.argv.slice(2);
  if (!["ko", "en"].includes(language) || !output) throw new Error("Use render-replay.js ko|en OUTPUT_DIRECTORY");
  const source = JSON.parse(await fs.readFile(path.join(root, "content/replay.json"), "utf8"));
  const chapters = JSON.parse(await fs.readFile(path.join(root, `content/chapters${language === "en" ? ".en" : ""}.json`), "utf8"));
  const base = JSON.parse(await fs.readFile(path.join(root, "content/chapters.json"), "utf8"));
  const titles = Object.fromEntries(chapters.map(chapter => [chapter.id, chapter.title]));
  const numbers = Object.fromEntries(base.map(chapter => [chapter.id, chapter.number]));
  await fs.mkdir(output, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  await page.route("**/*", route => route.abort());
  try {
    for (const [index, chapter] of source.chapters.entries()) {
      const label = `L${numbers[chapter.id]}`;
      const text = chapter[language];
      const surface = {
        terminal: language === "ko" ? "터미널 명령" : "Terminal commands",
        portal: language === "ko" ? "포털 경로 / 입력" : "Portal path / input",
        review: language === "ko" ? "시나리오와 실행 경계" : "Scenario and execution boundaries",
      }[chapter.surface];
      for (let step = 0; step < 3; step++) {
        const commands = chapter.commands_by_step ? chapter.commands_by_step[step] : chapter.commands;
        await page.setContent(`<!doctype html><html lang="${language}"><head><meta charset="utf-8"><style>
          *{box-sizing:border-box}body{margin:0;background:#081925;color:#e8f3f8;font-family:Arial,"Apple SD Gothic Neo",sans-serif}
          main{width:1920px;height:1080px;padding:58px 72px;position:relative}
          .brand{color:#66e0cb;font-size:24px;letter-spacing:3px}.top{display:flex;justify-content:space-between;align-items:center}
          .number{font-size:27px;color:#9eb9c8}h1{font-size:51px;margin:28px 0 32px;line-height:1.22;max-width:1760px}
          .layout{display:grid;grid-template-columns:560px 1fr;gap:44px;height:680px}.flow{display:flex;flex-direction:column;gap:20px}
          .step{border:2px solid #294656;border-radius:22px;padding:27px 24px;min-height:128px;display:flex;gap:22px;align-items:center;background:#102838}
          .step.active{border-color:#66e0cb;background:#153d46;box-shadow:0 0 0 5px #66e0cb14}
          .step b{font-size:38px;color:#66e0cb}.step span{font-size:29px;line-height:1.35}
          .boundary{margin-top:10px;font-size:24px;line-height:1.55;color:#a9c3d1}
          .terminal{border:2px solid #294656;border-radius:22px;background:#06121d;overflow:hidden}
          .bar{background:#142c3b;padding:21px 28px;font-size:23px;display:flex;justify-content:space-between;color:#abd5dc}
          pre{font-family:Menlo,Consolas,"Apple SD Gothic Neo",monospace;margin:0;padding:24px 30px;font-size:24px;line-height:1.5;white-space:pre-wrap;overflow-wrap:anywhere}
          .command{color:#e4f2fa}.command+.command{margin-top:16px}.prompt{color:#66e0cb}
          footer{position:absolute;bottom:36px;left:72px;right:72px;display:flex;justify-content:space-between;font-size:20px;color:#9ab6c5}
          .rail{position:absolute;bottom:0;left:0;height:8px;width:${100 * (index + 1) / source.chapters.length}%;background:#66e0cb}
        </style></head><body><main>
          <div class="top"><div class="brand">MICROSOFT FOUNDRY · CONTOSO LABS</div><div class="number">${String(index + 1).padStart(2, "0")} / ${source.chapters.length} · ${language.toUpperCase()}</div></div>
          <h1>${escape(label)} &nbsp; ${escape(titles[chapter.id])}</h1>
          <div class="layout"><div class="flow">${text.steps.map((value, i) => `<div class="step ${i === step ? "active" : ""}"><b>0${i + 1}</b><span>${escape(value)}</span></div>`).join("")}
          <div class="boundary">${language === "ko" ? "합성 데이터만 사용<br>실제 호출은 승인·범위·한도 확인 후<br>정답·승인·주문 완료를 가장하지 않기" : "Synthetic data only<br>Live calls require scope, approval, and bounds<br>Never fabricate correctness, approval, or ordering"}</div></div>
          <div class="terminal"><div class="bar"><span>● ● ● &nbsp; ${surface}</span><span>${escape(label)}</span></div>
          <pre>${commands.map(command => `<div class="command"><span class="prompt">${chapter.surface === "terminal" && /^(python|curl|azd|\.venv)/.test(command) ? "$ " : "› "}</span>${escape(command)}</div>`).join("")}</pre></div></div>
          <footer><span>${escape(source.notice[language])}</span><span>20 MODULES · READ → RUN → INSPECT</span></footer><div class="rail"></div>
        </main></body></html>`);
        await page.evaluate(() => document.fonts.ready);
        const layout = await page.evaluate(() => {
          const panel = document.querySelector(".terminal");
          const pre = document.querySelector("pre");
          while (pre.scrollHeight + document.querySelector(".bar").offsetHeight > panel.clientHeight - 8 && parseFloat(getComputedStyle(pre).fontSize) > 19) {
            pre.style.fontSize = `${parseFloat(getComputedStyle(pre).fontSize) - 1}px`;
          }
          return { overflow: pre.scrollHeight + document.querySelector(".bar").offsetHeight > panel.clientHeight, fontSize: getComputedStyle(pre).fontSize };
        });
        if (layout.overflow) throw new Error(`${language}/${chapter.id}: commands overflow the video frame`);
        await page.screenshot({ path: path.join(output, `${chapter.id}-${step}.png`) });
      }
    }
    console.log(`Rendered ${source.chapters.length * 3} ${language} frames at 1920x1080.`);
  } finally {
    await browser.close();
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
