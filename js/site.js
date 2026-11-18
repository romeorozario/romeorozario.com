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
  /* desktop renders at zoom 0.9 (see site.css): rects are in screen px, CSS lengths are not */
  var Z = function () { return parseFloat(getComputedStyle(doc).zoom) || 1; };

  /* ---------- Theme toggle with a circular reveal ---------- */
  function applyTheme(theme) {
    doc.setAttribute("data-theme", theme);
    try { sessionStorage.setItem("theme", theme); } catch (e) {}
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
      /* to light: light beams out of the toggle. To dark: the light shrinks from the
         screen edges back into the toggle, like the lights going out. */
      var toDark = next === "dark";
      var small = "circle(0px at " + x + "px " + y + "px)", full = "circle(" + radius + "px at " + x + "px " + y + "px)";
      doc.classList.add("theme-vt");
      doc.classList.toggle("theme-vt-out", toDark);
      var t = document.startViewTransition(function () { applyTheme(next); });
      t.ready.then(function () {
        if (toDark) {
          doc.animate({ clipPath: [full, small] },
            { duration: 700, easing: "cubic-bezier(0.55, 0, 0.45, 1)", fill: "forwards", pseudoElement: "::view-transition-old(root)" });
        } else {
          doc.animate({ clipPath: [small, full] },
            { duration: 750, easing: "cubic-bezier(0.22, 1, 0.36, 1)", pseudoElement: "::view-transition-new(root)" });
        }
      });
      t.finished.finally(function () { doc.classList.remove("theme-vt", "theme-vt-out"); });
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

  /* ---------- Rotating words (headline word, hero pill ticker) ----------
     The first phrase stays in the HTML for SEO and screen readers; the others
     slide through a mask. Options: data-rotate="a|b|c", data-rotate-every
     (ms between swaps), data-rotate-start (ms before the first swap). */
  document.querySelectorAll("[data-rotate]").forEach(function (rot) {
    if (still() || !rot.animate) return;
    var mask = rot.querySelector(".w") || rot;
    var cur = mask.firstElementChild;
    if (!cur) return;
    var words = [cur.textContent.trim()].concat(rot.getAttribute("data-rotate").split("|"));
    var every = +rot.getAttribute("data-rotate-every") || 2300;
    var start = +rot.getAttribute("data-rotate-start") || 2600;
    var idx = 0, timer = 0, visible = true, busy = false, off = false;
    var EASE_OUT = "cubic-bezier(0.65, 0, 0.35, 1)", EASE_IN = "cubic-bezier(0.22, 1, 0.36, 1)";
    cur.setAttribute("data-word", words[0]);
    mask.style.position = "relative";
    /* reserve the widest phrase so nothing reflows; if it cannot fit on one
       line (small phones), keep the first phrase still instead */
    var fit = function () {
      var probe = document.createElement("span");
      probe.style.cssText = "position:absolute;visibility:hidden;white-space:nowrap;left:0;top:0";
      mask.appendChild(probe);
      var w = 0;
      words.forEach(function (t) { probe.textContent = t; probe.setAttribute("data-word", t); w = Math.max(w, probe.getBoundingClientRect().width); });
      mask.removeChild(probe);
      var room = rot.getAttribute("data-rotate-room");
      var max = room ? rot.closest(room).parentNode.getBoundingClientRect().width - (+rot.getAttribute("data-rotate-pad") || 0) : Infinity;
      off = w > max;
      mask.style.width = off ? "" : Math.ceil(w / Z() + 2) + "px";
      mask.style.whiteSpace = off ? "" : "nowrap";
      if (off && idx !== 0) { mask.innerHTML = ""; cur = document.createElement("span"); cur.textContent = words[0]; mask.appendChild(cur); idx = 0; }
    };
    (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(fit);
    addEventListener("resize", fit);
    var schedule = function () { clearTimeout(timer); timer = setTimeout(swap, every); };
    var swap = function () {
      if (off || busy || !visible || document.hidden) return schedule();
      busy = true;
      idx = (idx + 1) % words.length;
      var next = document.createElement("span");
      next.textContent = words[idx];
      next.setAttribute("data-word", words[idx]);
      /* animation:none stops the headline's entrance keyframes (.w > span) from replaying on the new word */
      next.style.cssText = "position:absolute;left:0;top:0;display:inline-block;white-space:nowrap;animation:none;will-change:transform,opacity";
      mask.appendChild(next);
      var out = cur.animate([{ transform: "translate3d(0,0,0)", opacity: 1 }, { transform: "translate3d(0,-105%,0)", opacity: 0 }],
                            { duration: 420, easing: EASE_OUT, fill: "forwards" });
      var inn = next.animate([{ transform: "translate3d(0,105%,0) rotate(4deg)" }, { transform: "translate3d(0,0,0) rotate(0deg)" }],
                             { duration: 560, delay: 40, easing: EASE_IN, fill: "both" });
      Promise.all([out.finished, inn.finished]).then(function () {
        if (cur.parentNode) cur.parentNode.removeChild(cur);
        next.style.position = "static";
        next.style.willChange = "";
        inn.cancel();
        cur = next; busy = false; schedule();
      });
    };
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (en) { visible = en[0].isIntersecting; }).observe(rot);
    }
    timer = setTimeout(swap, start);
  });

  /* ---------- Scroll reveal with automatic stagger ---------- */
  document.querySelectorAll("[data-stagger]").forEach(function (group) {
    var n = 0;
    group.querySelectorAll("[data-reveal]").forEach(function (el) { el.style.setProperty("--i", Math.min(n++, 6)); });
  });
  var revealEls = document.querySelectorAll("[data-reveal]");
  if ("IntersectionObserver" in window && !still()) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("is-in"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px 12% 0px", threshold: 0 });
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

  /* ---------- Lightbox: images and videos grow out of their thumbnail ---------- */
  var zoomables = document.querySelectorAll("img[data-zoom], video[data-zoom]");
  if (zoomables.length && typeof HTMLDialogElement === "function") {
    var dlg = document.createElement("dialog");
    dlg.className = "lightbox";
    dlg.setAttribute("aria-label", "Enlarged view");
    dlg.innerHTML = '<img alt=""><video muted loop playsinline controls hidden></video><button type="button" class="close" aria-label="Close">×</button>';
    document.body.appendChild(dlg);
    var bigImg = dlg.querySelector("img"), bigVid = dlg.querySelector("video");
    var big = bigImg, source = null, closing = false;

    var flip = function (from, to, reverse) {
      var sx = from.width / to.width, sy = from.height / to.height;
      var z = Z(), dx = (from.left - to.left) / z, dy = (from.top - to.top) / z;
      var a = "translate(" + dx + "px, " + dy + "px) scale(" + sx + ", " + sy + ")";
      var b = "translate(0px, 0px) scale(1, 1)";
      return big.animate({ transform: reverse ? [b, a] : [a, b], borderRadius: reverse ? ["14px", "16px"] : ["16px", "14px"] },
        { duration: reverse ? 420 : 620, easing: "cubic-bezier(0.22, 1, 0.36, 1)", fill: "both" });
    };

    var open = function (el) {
      source = el;
      var isVid = el.tagName === "VIDEO";
      big = isVid ? bigVid : bigImg;
      bigImg.hidden = isVid; bigVid.hidden = !isVid;
      if (isVid) {
        bigVid.width = el.getAttribute("width") || el.videoWidth || 1280;
        bigVid.height = el.getAttribute("height") || el.videoHeight || 720;
        bigVid.poster = el.poster || "";
        bigVid.src = el.currentSrc || (el.querySelector("source") || {}).src;
        bigVid.setAttribute("aria-label", el.getAttribute("aria-label") || "Video");
        try { bigVid.currentTime = el.currentTime || 0; } catch (e) {}
        var p = bigVid.play(); if (p && p.catch) p.catch(function () {});
      } else {
        bigImg.src = el.currentSrc || el.src;
        bigImg.alt = el.alt;
      }
      dlg.showModal();
      requestAnimationFrame(function () { dlg.classList.add("is-open"); });
      if (still()) return;
      var go = function () {
        var anim = flip(el.getBoundingClientRect(), big.getBoundingClientRect(), false);
        anim.onfinish = function () { anim.cancel(); };
      };
      if (isVid || bigImg.complete) requestAnimationFrame(go); else bigImg.onload = go;
    };

    var close = function () {
      if (closing || !dlg.open) return;
      closing = true;
      dlg.classList.remove("is-open");
      var done = function () {
        dlg.close(); closing = false;
        if (big === bigVid) { bigVid.pause(); bigVid.removeAttribute("src"); bigVid.load(); } else bigImg.removeAttribute("src");
        if (source && source.isConnected) source.focus({ preventScroll: true });
      };
      if (still() || !source || !source.isConnected) { done(); return; }
      var anim = flip(source.getBoundingClientRect(), big.getBoundingClientRect(), true);
      anim.onfinish = function () { done(); anim.cancel(); };
    };

    zoomables.forEach(function (el) {
      var label = el.alt || el.getAttribute("aria-label") || "";
      el.setAttribute("tabindex", "0");
      el.setAttribute("role", "button");
      el.setAttribute("aria-label", (el.tagName === "VIDEO" ? "Play full size: " : "Enlarge image: ") + label);
      el.addEventListener("click", function (e) { e.preventDefault(); open(el); });
      el.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(el); } });
    });
    /* backdrop, the close button, or the image itself close it; a video keeps its own click for play and pause */
    dlg.addEventListener("click", function (e) { if (e.target === dlg || e.target === bigImg || e.target.classList.contains("close")) close(); });
    dlg.addEventListener("cancel", function (e) { e.preventDefault(); close(); });
  }

  /* ---------- Post slider: arrows drive native scroll-snap ---------- */
  document.querySelectorAll("[data-slider]").forEach(function (root) {
    var track = root.querySelector(".slider-track");
    var slides = Array.prototype.slice.call(track.children);
    var prev = root.querySelector(".arrow-btn.prev"), next = root.querySelector(".arrow-btn.next");
    var count = root.querySelector(".count");
    var step = function () {
      var w = slides[0].offsetWidth + parseFloat(getComputedStyle(track).columnGap || 18);
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

  /* ---------- Launch badges: fall back to a text chip if the platform image fails ---------- */
  document.querySelectorAll(".lbadge img").forEach(function (img) {
    var fallback = function () {
      var a = img.parentNode;
      a.classList.add("is-text");
      a.textContent = img.alt.replace(/^E-Warmup: /, "");
    };
    if (img.complete && img.naturalWidth === 0) fallback(); else img.addEventListener("error", fallback);
  });

  /* ---------- Photo stack: every few seconds the card underneath slides out
     from under the stack (past the frame edge) and lands on top ---------- */
  document.querySelectorAll("[data-stack]").forEach(function (stack) {
    var cards = Array.prototype.slice.call(stack.children);
    if (cards.length < 2) return;
    var every = +stack.getAttribute("data-stack-every") || 3000;
    /* the first (original) photo holds longer each time it is on top */
    var firstHold = +stack.getAttribute("data-stack-first") || every;
    var hold = function () { return order[0] === cards[0] ? firstHold : every; };
    var order = cards.slice();
    var paint = function () { order.forEach(function (c, i) { c.style.zIndex = String(order.length - i); }); };
    paint();
    if (still() || !stack.animate) return;
    var visible = true, busy = false, timer = 0;
    var EASE = "cubic-bezier(0.22, 1, 0.36, 1)";
    var cycle = function () {
      if (busy || !visible || document.hidden) return schedule();
      busy = true;
      var top = order[0], next = order[1];
      /* 1: the next card slides out from under the bottom-right edge */
      var out = next.animate(
        [{ transform: "translate3d(0,0,0) rotate(0deg)" }, { transform: "translate3d(44%, 3%, 0) rotate(4deg)" }],
        { duration: 750, easing: "cubic-bezier(0.33, 0, 0.2, 1)", fill: "forwards" });
      top.animate([{ transform: "scale(1)" }, { transform: "scale(0.96)" }], { duration: 750, easing: EASE, fill: "forwards" });
      out.finished.then(function () {
        /* 2: it moves to the front and settles into place */
        order.push(order.shift());
        order.splice(order.indexOf(next), 1); order.unshift(next);
        paint();
        var back = next.animate(
          [{ transform: "translate3d(44%, 3%, 0) rotate(4deg)" }, { transform: "translate3d(0,0,0) rotate(0deg)" }],
          { duration: 900, easing: EASE, fill: "forwards" });
        top.animate([{ transform: "scale(0.96)" }, { transform: "scale(1)" }], { duration: 900, easing: EASE, fill: "forwards" });
        back.finished.then(function () {
          cards.forEach(function (c) { c.getAnimations().forEach(function (a) { a.cancel(); }); });
          busy = false; schedule();
        });
      });
    };
    var schedule = function () { clearTimeout(timer); timer = setTimeout(cycle, hold()); };
    if ("IntersectionObserver" in window) new IntersectionObserver(function (en) { visible = en[0].isIntersecting; }).observe(stack);
    timer = setTimeout(cycle, firstHold + 1000);
  });

  /* ---------- Gallery pager: swipe or arrows between two-row photo pages ---------- */
  document.querySelectorAll("[data-gpager]").forEach(function (root) {
    var track = root.querySelector(".gp-track");
    var pages = Array.prototype.slice.call(track.children);
    var section = root.closest("section") || document;
    var prev = section.querySelector("[data-gp-prev]"), next = section.querySelector("[data-gp-next]");
    var count = section.querySelector("[data-gp-count]");
    var cur = -1;
    /* page positions include the gap between pages, so measure them instead of using clientWidth */
    var pos = function (i) { return pages[i].offsetLeft - pages[0].offsetLeft; };
    var index = function () {
      var best = 0, d = Infinity;
      pages.forEach(function (p, i) { var x = Math.abs(pos(i) - track.scrollLeft); if (x < d) { d = x; best = i; } });
      return best;
    };
    var update = function () {
      var i = Math.max(0, Math.min(pages.length - 1, index()));
      if (prev) prev.disabled = i === 0;
      if (next) next.disabled = i === pages.length - 1;
      if (count) count.textContent = (i + 1) + " / " + pages.length;
      if (i !== cur) {
        cur = i;
        pages.forEach(function (p, n) { p.inert = n !== i; });
      }
    };
    var go = function (d) {
      var i = Math.max(0, Math.min(pages.length - 1, index() + d));
      track.scrollTo({ left: pos(i), behavior: still() ? "auto" : "smooth" });
    };
    if (prev) prev.addEventListener("click", function () { go(-1); restart(); });
    if (next) next.addEventListener("click", function () { go(1); restart(); });
    /* auto-advance every data-gp-every ms (4000), looping; pauses on hover, touch,
       keyboard focus, when off-screen or the tab is hidden, and for reduced motion */
    var every = +root.getAttribute("data-gp-every") || 4000;
    var auto = 0, paused = false, onScreen = true;
    var tick = function () {
      if (paused || !onScreen || document.hidden) return;
      var i = index();
      track.scrollTo({ left: pos(i >= pages.length - 1 ? 0 : i + 1), behavior: "smooth" });
    };
    var restart = function () { clearInterval(auto); if (!still()) auto = setInterval(tick, every); };
    root.addEventListener("pointerenter", function (e) { if (e.pointerType === "mouse") paused = true; });
    root.addEventListener("pointerleave", function () { paused = false; restart(); });
    track.addEventListener("touchstart", function () { paused = true; }, { passive: true });
    track.addEventListener("touchend", function () { setTimeout(function () { paused = false; restart(); }, 1500); }, { passive: true });
    root.addEventListener("focusin", function () { paused = true; });
    root.addEventListener("focusout", function () { paused = false; restart(); });
    if ("IntersectionObserver" in window) new IntersectionObserver(function (en) { onScreen = en[0].isIntersecting; if (onScreen) restart(); }, { threshold: 0.3 }).observe(root);
    restart();
    track.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight") { e.preventDefault(); go(1); }
      if (e.key === "ArrowLeft") { e.preventDefault(); go(-1); }
    });
    var raf = 0;
    track.addEventListener("scroll", function () { cancelAnimationFrame(raf); raf = requestAnimationFrame(update); }, { passive: true });
    /* one fixed height for every page (the tallest), so content below never shifts */
    var fit = function () {
      track.style.height = "";
      var h = 0; pages.forEach(function (p) { h = Math.max(h, p.offsetHeight); });
      track.style.height = h + "px";
    };
    var refit = function () { fit(); cur = -1; update(); };
    addEventListener("resize", refit);
    pages.forEach(function (p) { p.querySelectorAll("img").forEach(function (im) { if (!im.complete) im.addEventListener("load", refit, { once: true }); }); });
    fit(); update();
  });

  /* ---------- Logo wall: even rows on tablet and phone ----------
     Below 1180px the three desktop rows flow as one wrapped group. Split the logos
     into rows of near-equal size (e.g. 21 logos: 7+7+7, 5+4+4+4+4, or 3 per row)
     so no logo ever sits alone on a row. */
  var wallMq = window.matchMedia("(max-width: 1180px)");
  var walls = document.querySelectorAll(".logo-wall");
  var balanceWalls = function () {
    walls.forEach(function (wall) {
      var items = wall.querySelectorAll(".logo-row > li");
      if (!wallMq.matches) { wall.classList.remove("is-balanced"); items.forEach(function (li) { li.style.removeProperty("--lw-b"); }); return; }
      var cs = getComputedStyle(wall);
      var w = (wall.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight)) / Z();
      var cell = innerWidth <= 680 ? 100 : 136;
      var n = items.length, max = Math.max(2, Math.floor(w / cell));
      var rows = Math.ceil(n / max);
      if (n > 1 && Math.floor(n / rows) < 2) rows = Math.floor(n / 2);
      var base = Math.floor(n / rows), extra = n % rows, i = 0;
      for (var r = 0; r < rows; r++) {
        var k = base + (r < extra ? 1 : 0);
        for (var j = 0; j < k; j++, i++) items[i].style.setProperty("--lw-b", (100 / k - 0.02).toFixed(3) + "%");
      }
      wall.classList.add("is-balanced");
    });
  };
  if (walls.length) {
    var lwRaf = 0;
    addEventListener("resize", function () { cancelAnimationFrame(lwRaf); lwRaf = requestAnimationFrame(balanceWalls); });
    balanceWalls();
  }

  /* ---------- DM menu (details[data-dm]): close on outside click, Esc, or after picking a link ---------- */
  document.querySelectorAll("details[data-dm]").forEach(function (d) {
    var sum = d.querySelector("summary");
    document.addEventListener("click", function (e) { if (d.open && !d.contains(e.target)) d.open = false; });
    d.addEventListener("keydown", function (e) { if (e.key === "Escape" && d.open) { d.open = false; sum.focus(); } });
    d.querySelectorAll("a").forEach(function (a) { a.addEventListener("click", function () { d.open = false; }); });
    /* open upwards when the section would clip the menu (the hero hides overflow for its glow) */
    d.addEventListener("toggle", function () {
      d.classList.remove("dm-up");
      if (!d.open) return;
      var pop = d.querySelector(".dm-pop"), clip = d.closest(".hero, section") || document.body;
      if (pop.getBoundingClientRect().bottom > clip.getBoundingClientRect().bottom - 8) d.classList.add("dm-up");
    });
  });

  /* ---------- Footer year ---------- */
  document.querySelectorAll("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
