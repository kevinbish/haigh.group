// Mobile menu, header border on scroll, gallery lightbox. No dependencies.
(function () {
  var btn = document.querySelector(".menu-btn");
  var nav = document.getElementById("nav");
  if (btn && nav) {
    btn.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      btn.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    });
    nav.addEventListener("click", function (e) {
      if (e.target.tagName === "A") { nav.classList.remove("open"); btn.setAttribute("aria-expanded", "false"); }
    });
  }

  var head = document.querySelector(".site-head");
  if (head) {
    var onScroll = function () { head.classList.toggle("scrolled", window.scrollY > 8); };
    window.addEventListener("scroll", onScroll, { passive: true }); onScroll();
  }

  // Scroll reveal — only when motion is allowed; content is visible without it.
  var calm = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!calm && "IntersectionObserver" in window) {
    document.documentElement.classList.add("js-motion");
    var groups = [".section-head", ".work > article", ".clients > figure", ".services > div",
                  ".news > li", ".team > div", ".contact .wrap > div", ".prose > figure", ".gallery"];
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
    }, { rootMargin: "0px 0px -8% 0px", threshold: .08 });
    groups.forEach(function (sel) {
      Array.prototype.forEach.call(document.querySelectorAll(sel), function (el, i) {
        el.classList.add("reveal");
        el.style.setProperty("--d", Math.min(i % 4, 3) * 0.09 + "s");   // gentle stagger within a row
        io.observe(el);
      });
    });
  }

  // Hero parallax: circles and dots lean toward the pointer (mouse/trackpad only, motion allowed).
  var hero = document.querySelector(".hero");
  if (hero && !calm && window.matchMedia("(pointer: fine)").matches) {
    var raf = 0;
    hero.addEventListener("pointermove", function (e) {
      if (raf) return;
      raf = requestAnimationFrame(function () {
        raf = 0;
        var r = hero.getBoundingClientRect();
        hero.style.setProperty("--mx", ((e.clientX - r.left) / r.width - .5).toFixed(3));
        hero.style.setProperty("--my", ((e.clientY - r.top) / r.height - .5).toFixed(3));
      });
    });
    hero.addEventListener("pointerleave", function () { hero.style.setProperty("--mx", 0); hero.style.setProperty("--my", 0); });
  }

  // Lightbox: links still open the full image if JS or <dialog> isn't available.
  var links = Array.prototype.slice.call(document.querySelectorAll(".gallery a"));
  if (!links.length || typeof HTMLDialogElement !== "function") return;
  var dlg = document.createElement("dialog");
  dlg.className = "lightbox";
  dlg.innerHTML = '<img alt=""><div class="lb-bar"><button type="button" data-step="-1">Previous</button>' +
    '<span class="lb-count"></span><button type="button" data-step="1">Next</button>' +
    '<button type="button" data-close>Close</button></div>';
  document.body.appendChild(dlg);
  var img = dlg.querySelector("img"), count = dlg.querySelector(".lb-count"), cur = 0, set = [];
  function show(i) {
    cur = (i + set.length) % set.length;
    img.src = set[cur].href;
    img.alt = set[cur].querySelector("img").alt;
    count.textContent = (cur + 1) + " of " + set.length;
  }
  links.forEach(function (a) {
    a.addEventListener("click", function (e) {
      e.preventDefault();
      set = Array.prototype.slice.call(a.closest(".gallery").querySelectorAll("a"));
      show(set.indexOf(a));
      dlg.showModal();
    });
  });
  dlg.addEventListener("click", function (e) {
    if (e.target === dlg || e.target.hasAttribute("data-close")) dlg.close();
    var step = e.target.getAttribute && e.target.getAttribute("data-step");
    if (step) show(cur + parseInt(step, 10));
  });
  document.addEventListener("keydown", function (e) {
    if (!dlg.open) return;
    if (e.key === "ArrowRight") show(cur + 1);
    if (e.key === "ArrowLeft") show(cur - 1);
  });
})();
