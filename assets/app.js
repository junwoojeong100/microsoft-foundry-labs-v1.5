(() => {
  "use strict";
  const data = JSON.parse(document.getElementById("guide-data").textContent);
  const pageMap = new Map(data.map(page => [page.id, page]));
  const labs = data.filter(page => page.track !== "reference");
  const key = "foundry-lab-guide-20260929";
  const search = document.getElementById("guide-search");
  const path = document.getElementById("learning-path");
  const sidebar = document.getElementById("sidebar");
  const menu = document.getElementById("menu-toggle");
  const results = document.getElementById("search-results");
  const list = document.getElementById("search-list");
  const hero = document.getElementById("hero");
  const quick = new Set(["l00", "l01", "l04", "l05", "l08", "l12", "instructor"]);
  const offline = new Set(["l00", "l01", "l06", "l08", "l12", "l15", "l18", "l20", "l21", "l22", "l23", "l24", "instructor", "troubleshooting"]);
  let activeId = "l00";
  let state = {done: [], theme: "light", path: "all"};
  let toastTimer;
  let printDetails = [];
  let printLinks = [];
  let printPrepared = false;

  function notify(message) {
    const toast = document.getElementById("toast");
    clearTimeout(toastTimer);
    toast.textContent = message;
    toast.classList.add("visible");
    toastTimer = setTimeout(() => toast.classList.remove("visible"), 4200);
  }

  function persist() {
    try {
      localStorage.setItem(key, JSON.stringify(state));
    } catch (error) {
      document.getElementById("storage-warning").hidden = false;
      console.warn("Progress storage unavailable:", error.name);
    }
  }

  try {
    const saved = JSON.parse(localStorage.getItem(key) || "null");
    if (saved && typeof saved === "object") {
      if (Array.isArray(saved.done)) state.done = [...new Set(saved.done.filter(id => labs.some(lab => lab.id === id)))];
      if (["light", "dark"].includes(saved.theme)) state.theme = saved.theme;
      if (["all", "core", "quick", "offline", "advanced", "reference"].includes(saved.path)) state.path = saved.path;
    }
  } catch (error) {
    document.getElementById("storage-warning").hidden = false;
    console.warn("Saved progress could not be read:", error.name);
  }

  function setTheme() {
    document.documentElement.dataset.theme = state.theme;
    const button = document.getElementById("theme-toggle");
    button.textContent = state.theme === "dark" ? "밝게" : "어둡게";
    button.setAttribute("aria-label", state.theme === "dark" ? "밝은 화면으로 전환" : "어두운 화면으로 전환");
  }

  function progress() {
    const done = new Set(state.done);
    document.getElementById("progress").value = done.size;
    document.getElementById("progress-label").textContent = `${done.size} / ${labs.length}`;
    document.querySelectorAll("[data-complete]").forEach(button => {
      const finished = done.has(button.dataset.complete);
      button.setAttribute("aria-pressed", String(finished));
      button.querySelector(".complete-label").textContent = finished ? "확인 완료 · 다시 누르면 해제" : "성공 기준을 확인했어요";
    });
    document.querySelectorAll(".chapter-link").forEach(link => link.classList.toggle("done", done.has(link.dataset.chapter)));
  }

  function inPath(page) {
    return state.path === "all" || page.track === state.path
      || (state.path === "quick" && quick.has(page.id))
      || (state.path === "offline" && offline.has(page.id));
  }

  function filterNavigation() {
    document.querySelectorAll(".chapter-link").forEach(link => {
      link.hidden = !inPath(pageMap.get(link.dataset.chapter));
    });
    document.querySelectorAll(".nav-group").forEach(group => {
      group.hidden = ![...group.querySelectorAll(".chapter-link")].some(link => !link.hidden);
    });
  }

  function closeMenu(returnFocus = false) {
    sidebar.classList.remove("open");
    document.body.classList.remove("no-scroll");
    menu.setAttribute("aria-expanded", "false");
    if (returnFocus) menu.focus();
  }

  function showPage(focus = false) {
    let hash;
    try {
      hash = decodeURIComponent(location.hash.slice(1));
    } catch (error) {
      if (!(error instanceof URIError)) throw error;
      hash = "";
      notify("올바르지 않은 주소 조각입니다. 시작 모듈로 이동했습니다.");
    }
    const target = document.getElementById(hash);
    const article = target && (target.matches(".chapter") ? target : target.closest(".chapter"));
    const id = article ? article.id : "l00";
    activeId = id;
    search.value = "";
    results.hidden = true;
    document.querySelectorAll(".chapter").forEach(page => page.classList.toggle("active", page.id === id));
    hero.hidden = id !== "l00";
    if (!inPath(pageMap.get(id))) {
      state.path = "all";
      path.value = "all";
      persist();
    }
    filterNavigation();
    document.querySelectorAll(".chapter-link").forEach(link => {
      if (link.dataset.chapter === id) link.setAttribute("aria-current", "page");
      else link.removeAttribute("aria-current");
    });
    closeMenu();
    document.title = `${pageMap.get(id).title} | Microsoft Foundry 실습 가이드`;
    if (focus) {
      const heading = document.getElementById(`${id}-title`);
      if (target && target !== article) {
        target.scrollIntoView({block: "start", behavior: "auto"});
      } else {
        const destination = id === "l00" ? hero : article;
        destination.scrollIntoView({block: "start", behavior: "auto"});
        heading.focus({preventScroll: true});
      }
    }
  }

  function runSearch() {
    const query = search.value.trim().toLocaleLowerCase();
    if (!query) {
      showPage();
      return;
    }
    const terms = query.split(/\s+/);
    const matched = data.filter(page => inPath(page) && terms.every(term =>
      `${page.title} ${page.summary} ${page.text}`.toLocaleLowerCase().includes(term)
    ));
    document.querySelectorAll(".chapter").forEach(page => page.classList.remove("active"));
    hero.hidden = true;
    results.hidden = false;
    list.replaceChildren();
    document.getElementById("search-count").textContent = matched.length
      ? `선택한 학습 경로에서 ${matched.length}개 모듈을 찾았습니다.`
      : "일치하는 모듈이 없습니다. 검색어를 줄이거나 학습 경로를 전체로 바꿔보세요.";
    matched.forEach(page => {
      const link = document.createElement("a");
      link.className = "search-result";
      link.href = `#${page.id}`;
      const label = document.createElement("small");
      label.textContent = page.track === "reference" ? `참고 ${page.number}` : `LAB ${page.number}`;
      const title = document.createElement("strong");
      title.textContent = page.title;
      const snippet = document.createElement("p");
      const position = page.text.toLocaleLowerCase().indexOf(terms[0]);
      const start = Math.max(0, position - 35);
      snippet.textContent = (start ? "… " : "") + page.text.slice(start, start + 180) + " …";
      link.append(label, title, snippet);
      link.addEventListener("click", () => {
        if (location.hash === `#${page.id}`) showPage(true);
      });
      list.append(link);
    });
  }

  function preparePrint(mode) {
    if (printPrepared) return;
    printPrepared = true;
    document.body.dataset.print = mode;
    printDetails = [...document.querySelectorAll("details")].map(node => [node, node.open]);
    printDetails.forEach(([node]) => { node.open = true; });
    printLinks = [...document.querySelectorAll('a[href]')]
      .map(node => [node, node.getAttribute("href")])
      .filter(([, href]) => !/^(https?:|#)/.test(href) || pageMap.has(href.slice(1)));
    printLinks.forEach(([node, href]) => {
      if (href.startsWith("#") && pageMap.has(href.slice(1))) node.setAttribute("href", `${href}-title`);
      else node.removeAttribute("href");
    });
    document.getElementById(activeId).classList.add("active");
  }

  function restorePrint() {
    printDetails.forEach(([node, open]) => { node.open = open; });
    printDetails = [];
    printLinks.forEach(([node, href]) => node.setAttribute("href", href));
    printLinks = [];
    printPrepared = false;
    delete document.body.dataset.print;
    if (search.value.trim()) runSearch();
  }

  document.querySelectorAll("pre > code").forEach(code => {
    const pre = code.parentElement;
    const label = document.createElement("span");
    label.className = "code-label";
    label.textContent = (code.className.match(/language-([\w-]+)/) || [null, "TEXT"])[1];
    label.setAttribute("aria-hidden", "true");
    const button = document.createElement("button");
    button.type = "button";
    button.className = "copy-button";
    button.textContent = "복사";
    button.setAttribute("aria-label", "이 코드 블록 복사");
    button.addEventListener("click", async () => {
      try {
        if (!navigator.clipboard) throw new Error("ClipboardUnavailable");
        await navigator.clipboard.writeText(code.textContent);
        notify("코드를 복사했습니다. 값과 비용 발생 여부를 확인한 뒤 실행하세요.");
      } catch (error) {
        const range = document.createRange();
        range.selectNodeContents(code);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        notify("자동 복사가 제한되어 텍스트를 선택했습니다. Ctrl+C 또는 Command+C로 복사하세요.");
      }
    });
    pre.append(label, button);
  });

  document.querySelectorAll("[data-complete]").forEach(button => button.addEventListener("click", () => {
    const id = button.dataset.complete;
    state.done = state.done.includes(id) ? state.done.filter(item => item !== id) : [...state.done, id];
    persist();
    progress();
    notify("학습 진도를 저장했습니다. Azure 실행 여부는 별도 기록표에 남기세요.");
  }));
  document.getElementById("theme-toggle").addEventListener("click", () => {
    state.theme = state.theme === "light" ? "dark" : "light";
    setTheme();
    persist();
  });
  document.getElementById("reset-progress").addEventListener("click", () => {
    if (!window.confirm("이 브라우저의 학습 체크만 초기화합니다. Azure 자원이나 파일은 삭제되지 않습니다. 초기화할까요?")) return;
    state.done = [];
    persist();
    progress();
    notify("이 브라우저의 학습 진도를 초기화했습니다.");
  });
  path.value = state.path;
  path.addEventListener("change", () => {
    state.path = path.value;
    persist();
    filterNavigation();
    if (search.value.trim()) runSearch();
    else notify(state.path === "offline" ? "Azure 없이 가능한 일부 로컬·설계 단계를 모았습니다. 각 모듈의 실행 조건을 확인하세요." : "목차를 선택한 학습 경로로 표시했습니다.");
  });
  search.addEventListener("input", runSearch);
  search.addEventListener("keydown", event => {
    if (event.key === "Enter") {
      const first = list.querySelector("a");
      if (!results.hidden && first) { event.preventDefault(); first.click(); }
    }
  });
  menu.addEventListener("click", () => {
    const open = !sidebar.classList.contains("open");
    sidebar.classList.toggle("open", open);
    document.body.classList.toggle("no-scroll", open);
    menu.setAttribute("aria-expanded", String(open));
    if (open) search.focus();
  });
  document.addEventListener("keydown", event => {
    const editing = event.target.matches("input, textarea, select, [contenteditable]");
    if ((event.key === "/" && !editing) || ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k")) {
      event.preventDefault();
      if (window.matchMedia("(max-width: 850px)").matches) {
        sidebar.classList.add("open");
        menu.setAttribute("aria-expanded", "true");
        document.body.classList.add("no-scroll");
      }
      search.focus();
      search.select();
    }
    if (event.key === "Escape") {
      if (search.value) { search.value = ""; showPage(); }
      else closeMenu(true);
    }
    if (event.key === "Tab" && sidebar.classList.contains("open")) {
      const focusables = [menu, ...sidebar.querySelectorAll("input, select, button, a[href]")].filter(node => node.getClientRects().length);
      const first = focusables[0], last = focusables[focusables.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    }
  });
  document.getElementById("main").addEventListener("click", () => closeMenu());
  document.querySelectorAll(".chapter-link").forEach(link => link.addEventListener("click", () => {
    if (location.hash === link.getAttribute("href")) showPage(true);
  }));
  window.matchMedia("(max-width: 850px)").addEventListener("change", event => { if (!event.matches) closeMenu(); });
  window.addEventListener("hashchange", () => showPage(true));
  document.getElementById("print-one").addEventListener("click", () => { preparePrint("one"); window.print(); });
  document.getElementById("print-all").addEventListener("click", () => { preparePrint("all"); window.print(); });
  window.addEventListener("beforeprint", () => preparePrint(document.body.dataset.print || "one"));
  window.addEventListener("afterprint", restorePrint);
  document.documentElement.classList.add("js");
  setTheme();
  progress();
  showPage(false);
})();
