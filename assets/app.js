(() => {
  "use strict";
  const data = JSON.parse(document.getElementById("guide-data").textContent);
  const ui = JSON.parse(document.getElementById("guide-ui").textContent);
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
    button.textContent = state.theme === "dark" ? ui.light : ui.dark;
    button.setAttribute("aria-label", state.theme === "dark" ? ui.light_aria : ui.dark_aria);
  }

  function progress() {
    const done = new Set(state.done);
    document.getElementById("progress").value = done.size;
    document.getElementById("progress-label").textContent = `${done.size} / ${labs.length}`;
    document.querySelectorAll("[data-complete]").forEach(button => {
      const finished = done.has(button.dataset.complete);
      button.setAttribute("aria-pressed", String(finished));
      button.querySelector(".complete-label").textContent = finished ? ui.completed : ui.complete;
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

  function updatePagination() {
    const pages = data.filter(inPath);
    const index = pages.findIndex(page => page.id === activeId);
    const navigation = document.querySelector(`#${activeId} .chapter-pagination`);
    const link = (page, label, next = false) => {
      const node = document.createElement("a");
      node.href = `#${page.id}`;
      if (next) node.className = "next";
      const caption = document.createElement("span");
      caption.textContent = label;
      node.append(caption, document.createTextNode(page.title));
      return node;
    };
    navigation.replaceChildren(
      index > 0 ? link(pages[index - 1], ui.previous) : document.createElement("span"),
      index >= 0 && index + 1 < pages.length
        ? link(pages[index + 1], ui.next, true)
        : link(pageMap.get("l00"), ui.back, true),
    );
  }

  function showPage(focus = false) {
    let hash;
    try {
      hash = decodeURIComponent(location.hash.slice(1));
    } catch (error) {
      if (!(error instanceof URIError)) throw error;
      hash = "";
      notify(ui.invalid_hash);
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
    updatePagination();
    if (article && target !== article) {
      for (let parent = target.parentElement; parent && parent !== article; parent = parent.parentElement) {
        if (parent.tagName === "DETAILS") parent.open = true;
      }
    }
    document.querySelectorAll(".chapter-link").forEach(link => {
      if (link.dataset.chapter === id) link.setAttribute("aria-current", "page");
      else link.removeAttribute("aria-current");
    });
    closeMenu();
    document.title = `${pageMap.get(id).title} | ${ui.title}`;
    document.querySelectorAll("[data-language]").forEach(link => {
      link.setAttribute("href", `${link.getAttribute("href").split("#")[0]}#${id}`);
    });
    if (focus || (article && target !== article)) {
      const heading = document.getElementById(`${id}-title`);
      if (target && target !== article) {
        target.scrollIntoView({block: "start", behavior: "auto"});
        target.setAttribute("tabindex", "-1");
        target.focus({preventScroll: true});
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
      ? ui.search_found.replace("{count}", matched.length)
      : ui.search_empty;
    matched.forEach(page => {
      const link = document.createElement("a");
      link.className = "search-result";
      link.href = `#${page.id}`;
      const label = document.createElement("small");
      label.textContent = page.track === "reference" ? `${ui.reference} ${page.number}` : `LAB ${page.number}`;
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
    const language = (code.className.match(/language-([\w-]+)/) || [null, "text"])[1];
    label.textContent = ui.code_labels[language] || language;
    label.title = language;
    label.setAttribute("aria-hidden", "true");
    const button = document.createElement("button");
    button.type = "button";
    button.className = "copy-button";
    button.textContent = ui.copy;
    button.setAttribute("aria-label", ui.copy_aria);
    button.addEventListener("click", async () => {
      try {
        if (!navigator.clipboard) throw new Error("ClipboardUnavailable");
        await navigator.clipboard.writeText(code.textContent);
        notify(ui.copied);
      } catch (error) {
        const range = document.createRange();
        range.selectNodeContents(code);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        notify(ui.copy_fallback);
      }
    });
    pre.append(label, button);
  });

  document.querySelectorAll("[data-complete]").forEach(button => button.addEventListener("click", () => {
    const id = button.dataset.complete;
    state.done = state.done.includes(id) ? state.done.filter(item => item !== id) : [...state.done, id];
    persist();
    progress();
    notify(ui.progress_saved);
  }));
  document.getElementById("theme-toggle").addEventListener("click", () => {
    state.theme = state.theme === "light" ? "dark" : "light";
    setTheme();
    persist();
  });
  document.getElementById("reset-progress").addEventListener("click", () => {
    if (!window.confirm(ui.reset_confirm)) return;
    state.done = [];
    persist();
    progress();
    notify(ui.reset_done);
  });
  path.value = state.path;
  path.addEventListener("change", () => {
    state.path = path.value;
    persist();
    filterNavigation();
    if (search.value.trim()) runSearch();
    else {
      if (!inPath(pageMap.get(activeId))) location.hash = data.find(inPath).id;
      else updatePagination();
      notify(state.path === "offline" ? ui.offline_path : ui.path_selected);
    }
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
