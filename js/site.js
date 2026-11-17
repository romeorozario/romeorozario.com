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

  /* ---------- Footer year ---------- */
  document.querySelectorAll("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
