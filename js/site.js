/* =====================================================================
   romeorozario.com: shared interactions
   No dependencies. Everything here is progressive enhancement: the page
   is fully readable with JavaScript off.
   ===================================================================== */
(function () {
  "use strict";

  var doc = document.documentElement;
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  var finePointer = window.matchMedia("(hover: hover) and (pointer: fine)");
  var still = function () { return reduceMotion.matches; };

  /* ---------- Theme toggle with a circular reveal ---------- */
  function applyTheme(theme) {
    doc.setAttribute("data-theme", theme);
    try { localStorage.setItem("theme", theme); } catch (e) {}
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", theme === "dark" ? "#070C1A" : "#F6F7FB");
    document.querySelectorAll("[data-theme-toggle]").forEach(function (b) {
      b.setAttribute("aria-label", theme === "dark" ? "Switch to light mode" : "Switch to dark mode");
      b.setAttribute("aria-pressed", theme === "dark" ? "true" : "false");
    });
  }
  applyTheme(doc.getAttribute("data-theme") === "dark" ? "dark" : "light");

  document.querySelectorAll("[data-theme-toggle]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var next = doc.getAttribute("data-theme") === "dark" ? "light" : "dark";
      if (!document.startViewTransition || still()) { applyTheme(next); return; }
      var r = btn.getBoundingClientRect();
      var x = r.left + r.width / 2, y = r.top + r.height / 2;
      var radius = Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y));
      doc.classList.add("theme-vt");
      var t = document.startViewTransition(function () { applyTheme(next); });
      t.ready.then(function () {
        doc.animate(
          { clipPath: ["circle(0px at " + x + "px " + y + "px)", "circle(" + radius + "px at " + x + "px " + y + "px)"] },
          { duration: 750, easing: "cubic-bezier(0.22, 1, 0.36, 1)", pseudoElement: "::view-transition-new(root)" }
        );
      });
      t.finished.finally(function () { doc.classList.remove("theme-vt"); });
    });
  });

  /* ---------- Header: hide on scroll down, show on scroll up ---------- */
  var header = document.querySelector(".site-header");
  var navLinks = document.querySelector(".nav-links");
  var menuBtn = document.querySelector(".menu-toggle");
  if (header) {
    var lastY = scrollY, ticking = false;
    var onScroll = function () {
      var y = scrollY;
      header.classList.toggle("is-scrolled", y > 8);
      var menuOpen = navLinks && navLinks.classList.contains("is-open");
      if (!menuOpen && y > 240 && y > lastY + 4) header.classList.add("is-hidden");
      else if (y < lastY - 4 || y < 240) header.classList.remove("is-hidden");
      lastY = y; ticking = false;
    };
    addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
    header.addEventListener("focusin", function () { header.classList.remove("is-hidden"); });
    onScroll();
  }

  /* ---------- Mobile menu ---------- */
  if (menuBtn && navLinks) {
    var setMenu = function (open) {
      navLinks.classList.toggle("is-open", open);
      menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
    };
    menuBtn.addEventListener("click", function () { setMenu(!navLinks.classList.contains("is-open")); });
    navLinks.addEventListener("click", function (e) { if (e.target.closest("a")) setMenu(false); });
    var menuY = 0;
    menuBtn.addEventListener("click", function () { menuY = scrollY; });
    addEventListener("scroll", function () {
      if (navLinks.classList.contains("is-open") && Math.abs(scrollY - menuY) > 60) setMenu(false);
    }, { passive: true });
    addEventListener("keydown", function (e) { if (e.key === "Escape") setMenu(false); });
  }

  /* ---------- Headline: split into words for a masked slide-up ---------- */
  document.querySelectorAll("[data-split]").forEach(function (el) {
    var i = 0;
    var walk = function (node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (child) {
        if (child.nodeType === 3) {
          var frag = document.createDocumentFragment();
          child.textContent.split(/(\s+)/).forEach(function (part) {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(" ")); return; }
            var w = document.createElement("span"); w.className = "w";
            var inner = document.createElement("span"); inner.textContent = part; inner.style.setProperty("--i", i++);
            w.appendChild(inner); frag.appendChild(w);
          });
          node.replaceChild(frag, child);
        } else if (child.nodeType === 1) { walk(child); }
      });
    };
    el.setAttribute("aria-label", el.textContent.replace(/\s+/g, " ").trim());
    walk(el);
    el.querySelectorAll(".w").forEach(function (w) { w.setAttribute("aria-hidden", "true"); });
    el.classList.add("is-split");
  });

  /* ---------- Scroll reveal with automatic stagger ---------- */
  document.querySelectorAll("[data-stagger]").forEach(function (group) {
    var n = 0;
    group.querySelectorAll("[data-reveal]").forEach(function (el) { el.style.setProperty("--i", Math.min(n++, 8)); });
  });
  var revealEls = document.querySelectorAll("[data-reveal]");
  if ("IntersectionObserver" in window && !still()) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("is-in"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.12 });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add("is-in"); });
  }

  /* ---------- Count-up numbers ---------- */
  var counters = document.querySelectorAll("[data-count]");
  var runCount = function (el) {
    var target = parseFloat(el.getAttribute("data-count"));
    var prefix = el.getAttribute("data-prefix") || "";
    var suffix = el.getAttribute("data-suffix") || "";
    var dur = 1600, start = performance.now();
    var fmt = function (v) { return prefix + Math.round(v).toLocaleString("en-US") + suffix; };
    var tick = function (now) {
      var p = Math.min(1, (now - start) / dur);
      var eased = 1 - Math.pow(1 - p, 4);
      el.textContent = fmt(target * eased);
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  };
  if ("IntersectionObserver" in window && !still()) {
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { runCount(en.target); cio.unobserve(en.target); } });
    }, { threshold: 0.6 });
    counters.forEach(function (el) { cio.observe(el); });
  }

  /* ---------- Magnetic buttons (mouse and trackpad only) ---------- */
  if (finePointer.matches && !still()) {
    document.querySelectorAll("[data-magnetic]").forEach(function (el) {
      el.addEventListener("pointermove", function (e) {
        var r = el.getBoundingClientRect();
        var dx = (e.clientX - (r.left + r.width / 2)) / (r.width / 2);
        var dy = (e.clientY - (r.top + r.height / 2)) / (r.height / 2);
        el.style.setProperty("--bx", (dx * 6).toFixed(2) + "px");
        el.style.setProperty("--by", (dy * 5).toFixed(2) + "px");
      });
      el.addEventListener("pointerleave", function () {
        el.style.setProperty("--bx", "0px");
        el.style.setProperty("--by", "0px");
      });
    });
  }

  /* ---------- Lightbox: the image grows out of its thumbnail ---------- */
  var zoomables = document.querySelectorAll("img[data-zoom]");
  if (zoomables.length && typeof HTMLDialogElement === "function") {
    var dlg = document.createElement("dialog");
    dlg.className = "lightbox";
    dlg.setAttribute("aria-label", "Enlarged image");
    dlg.innerHTML = '<img alt=""><button type="button" class="close" aria-label="Close">×</button>';
    document.body.appendChild(dlg);
    var big = dlg.querySelector("img");
    var source = null, closing = false;

    var flip = function (from, to, reverse) {
      var sx = from.width / to.width, sy = from.height / to.height;
      var dx = from.left - to.left, dy = from.top - to.top;
      var a = "translate(" + dx + "px, " + dy + "px) scale(" + sx + ", " + sy + ")";
      var b = "translate(0px, 0px) scale(1, 1)";
      return big.animate({ transform: reverse ? [b, a] : [a, b], borderRadius: reverse ? ["14px", "16px"] : ["16px", "14px"] },
        { duration: reverse ? 420 : 620, easing: "cubic-bezier(0.22, 1, 0.36, 1)", fill: "both" });
    };

    var open = function (img) {
      source = img;
      big.src = img.currentSrc || img.src;
      big.alt = img.alt;
      dlg.showModal();
      requestAnimationFrame(function () { dlg.classList.add("is-open"); });
      if (still()) return;
      var go = function () {
        var anim = flip(img.getBoundingClientRect(), big.getBoundingClientRect(), false);
        anim.onfinish = function () { anim.cancel(); };
      };
      if (big.complete) go(); else big.onload = go;
    };

    var close = function () {
      if (closing || !dlg.open) return;
      closing = true;
      dlg.classList.remove("is-open");
      var done = function () { dlg.close(); closing = false; big.removeAttribute("src"); if (source && source.isConnected) source.focus({ preventScroll: true }); };
      if (still() || !source || !source.isConnected) { done(); return; }
      var anim = flip(source.getBoundingClientRect(), big.getBoundingClientRect(), true);
      anim.onfinish = function () { done(); anim.cancel(); };
    };

    zoomables.forEach(function (img) {
      img.setAttribute("tabindex", "0");
      img.setAttribute("role", "button");
      img.setAttribute("aria-label", "Enlarge image: " + img.alt);
      img.addEventListener("click", function (e) { e.preventDefault(); open(img); });
      img.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(img); } });
    });
    dlg.addEventListener("click", function (e) { if (e.target === dlg || e.target === big || e.target.classList.contains("close")) close(); });
    dlg.addEventListener("cancel", function (e) { e.preventDefault(); close(); });
  }

  /* ---------- Post slider: arrows drive native scroll-snap ---------- */
  document.querySelectorAll("[data-slider]").forEach(function (root) {
    var track = root.querySelector(".slider-track");
    var slides = Array.prototype.slice.call(track.children);
    var prev = root.querySelector(".arrow-btn.prev"), next = root.querySelector(".arrow-btn.next");
    var count = root.querySelector(".count");
    var step = function () {
      var w = slides[0].getBoundingClientRect().width + parseFloat(getComputedStyle(track).columnGap || 18);
      return Math.max(1, Math.floor(track.clientWidth / w)) * w;
    };
    var update = function () {
      var max = track.scrollWidth - track.clientWidth - 2;
      if (prev) prev.disabled = track.scrollLeft <= 2;
      if (next) next.disabled = track.scrollLeft >= max;
      var tr = track.getBoundingClientRect(), seen = 0;
      slides.forEach(function (sl) {
        var r = sl.getBoundingClientRect();
        var full = r.left >= tr.left - 2 && r.right <= tr.right + 2;
        sl.classList.toggle("is-peek", !full && r.left < tr.right && r.right > tr.left);
        if (r.right <= tr.right + 2) seen++;
      });
      if (count) count.textContent = Math.min(seen, slides.length) + " of " + slides.length + " posts";
    };
    if (prev) prev.addEventListener("click", function () { track.scrollBy({ left: -step(), behavior: still() ? "auto" : "smooth" }); });
    if (next) next.addEventListener("click", function () { track.scrollBy({ left: step(), behavior: still() ? "auto" : "smooth" }); });
    var raf = 0;
    track.addEventListener("scroll", function () { cancelAnimationFrame(raf); raf = requestAnimationFrame(update); }, { passive: true });
    addEventListener("resize", update);
    update();
  });

  /* ---------- Pager: pages of cards that slide in and out ---------- */
  document.querySelectorAll("[data-pager]").forEach(function (root) {
    var pages = root.querySelectorAll(".pager-page");
    var prev = root.querySelector(".arrow-btn.prev"), next = root.querySelector(".arrow-btn.next");
    var label = root.parentNode.querySelector("[data-pager-label]");
    var cur = 0;
    var show = function (n, dir) {
      pages.forEach(function (pg, i) {
        pg.classList.remove("from-left", "from-right");
        if (i === n) { pg.classList.add("is-current"); pg.removeAttribute("aria-hidden"); pg.inert = false; }
        else {
          if (pg.classList.contains("is-current")) pg.classList.add(dir > 0 ? "from-left" : "from-right");
          pg.classList.remove("is-current"); pg.setAttribute("aria-hidden", "true"); pg.inert = true;
        }
      });
      if (dir) {
        var incoming = pages[n];
        incoming.classList.add(dir > 0 ? "from-right" : "from-left");
        incoming.getBoundingClientRect();
        incoming.classList.remove("from-right", "from-left");
      }
      cur = n;
      if (prev) prev.disabled = n === 0;
      if (next) next.disabled = n === pages.length - 1;
      if (label) label.textContent = (n + 1) + " / " + pages.length;
    };
    var toTop = function () {
      var top = root.getBoundingClientRect().top;
      if (top < 0) scrollBy({ top: top - 120, behavior: still() ? "auto" : "smooth" });
    };
    if (prev) prev.addEventListener("click", function () { if (cur > 0) { show(cur - 1, -1); toTop(); } });
    if (next) next.addEventListener("click", function () { if (cur < pages.length - 1) { show(cur + 1, 1); toTop(); } });
    show(0, 0);
  });

  /* ---------- Jump nav: highlight the section in view ---------- */
  var jump = document.querySelector("[data-jump]");
  if (jump && "IntersectionObserver" in window) {
    var links = jump.querySelectorAll("a[href^='#']");
    var map = {};
    links.forEach(function (a) { var sec = document.getElementById(a.getAttribute("href").slice(1)); if (sec) map[sec.id] = a; });
    var setActive = function (id) {
      links.forEach(function (a) { a.classList.toggle("is-active", map[id] === a); });
      var a = map[id];
      if (a) {
        var bar = a.parentNode, left = a.offsetLeft - bar.clientWidth / 2 + a.clientWidth / 2;
        bar.scrollTo({ left: left, behavior: still() ? "auto" : "smooth" });
      }
    };
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) setActive(en.target.id); });
    }, { rootMargin: "-40% 0px -55% 0px" });
    Object.keys(map).forEach(function (id) { spy.observe(document.getElementById(id)); });
  }

  /* ---------- Click-to-play YouTube and Spotify (no heavy embeds until asked) ---------- */
  document.querySelectorAll("[data-yt]").forEach(function (a) {
    a.addEventListener("click", function (e) {
      if (e.metaKey || e.ctrlKey || e.shiftKey) return;
      e.preventDefault();
      var frame = a.querySelector(".frame");
      if (frame.querySelector("iframe")) return;
      var f = document.createElement("iframe");
      f.src = "https://www.youtube-nocookie.com/embed/" + a.getAttribute("data-yt") + "?autoplay=1&rel=0";
      f.title = a.getAttribute("aria-label") || "YouTube video";
      f.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share";
      f.allowFullscreen = true;
      frame.appendChild(f);
    });
  });
  document.querySelectorAll("[data-spotify]").forEach(function (a) {
    a.addEventListener("click", function (e) {
      if (e.metaKey || e.ctrlKey || e.shiftKey) return;
      e.preventDefault();
      var box = document.createElement("div");
      box.className = "sp-embed";
      box.innerHTML = '<iframe loading="lazy" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" title="' +
        (a.getAttribute("aria-label") || "Spotify player") + '" src="https://open.spotify.com/embed/artist/' + a.getAttribute("data-spotify") + '?utm_source=generator"></iframe>';
      a.replaceWith(box);
    });
  });

  /* ---------- Muted videos play while on screen, pause when off ---------- */
  var vids = document.querySelectorAll("video[data-autoplay]");
  if (vids.length && "IntersectionObserver" in window && !still()) {
    var vio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        var v = en.target;
        if (en.isIntersecting) { v.preload = "auto"; var p = v.play(); if (p && p.catch) p.catch(function () {}); }
        else if (!v.paused) v.pause();
      });
    }, { threshold: 0.5 });
    vids.forEach(function (v) { vio.observe(v); });
  }

  /* ---------- Footer year ---------- */
  document.querySelectorAll("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
