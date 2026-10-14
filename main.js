// Site script: nav, reveal, hero demo, method loop, pricing toggle, calculator, report card form.
(function () {
  "use strict";
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Reveal sections as they scroll in
  var reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && !reduceMotion) {
    document.documentElement.classList.add("js");
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
    }, { rootMargin: "0px 0px -8% 0px" });
    reveals.forEach(function (el) { io.observe(el); });
  }

  // Method: light Answer, Rank, Repeat in turn
  document.querySelectorAll("[data-method]").forEach(function (box) {
    var n = 0;
    var light = function () {
      box.querySelectorAll("[data-phase]").forEach(function (el) { el.classList.toggle("lit", el.getAttribute("data-phase") === String(n)); });
    };
    light();
    if (!reduceMotion) setInterval(function () { n = (n + 1) % 3; light(); }, 2600);
  });

  // Nav: mobile toggle and dropdowns
  var head = document.querySelector(".site-head");
  var toggle = document.querySelector(".nav-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var open = head.classList.toggle("nav-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }
  var groups = document.querySelectorAll(".nav-group");
  groups.forEach(function (g) {
    var btn = g.querySelector("button");
    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      var open = !g.classList.contains("open");
      groups.forEach(function (o) { o.classList.remove("open"); o.querySelector("button").setAttribute("aria-expanded", "false"); });
      if (open) { g.classList.add("open"); btn.setAttribute("aria-expanded", "true"); }
    });
  });
  document.addEventListener("click", function () { groups.forEach(function (g) { g.classList.remove("open"); }); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") groups.forEach(function (g) { g.classList.remove("open"); }); });

  // Hero demo: four coded scenes on a loop
  var demo = document.querySelector(".demo");
  if (demo) {
    var scenes = demo.querySelectorAll(".scene");
    var steps = demo.querySelectorAll(".demo-steps button");
    var ms = 3800, i = 0, timer = null;
    demo.style.setProperty("--scene-ms", ms + "ms");
    var show = function (n) {
      i = n;
      scenes.forEach(function (s, k) { s.classList.toggle("on", k === n); });
      steps.forEach(function (b, k) {
        b.classList.remove("active", "done");
        void b.offsetWidth; // restart the progress fill
        if (k < n) b.classList.add("done");
        if (k === n) b.classList.add(reduceMotion ? "done" : "active");
      });
    };
    var run = function () {
      clearTimeout(timer);
      if (reduceMotion) return;
      timer = setTimeout(function () { show((i + 1) % scenes.length); run(); }, ms);
    };
    steps.forEach(function (b, k) { b.addEventListener("click", function () { show(k); run(); }); });
    show(0); run();
  }

  // The loop: light each stop in turn
  var stops = document.querySelectorAll(".loop-stop");
  if (stops.length && !reduceMotion) {
    var s = 0;
    stops[0].classList.add("lit");
    setInterval(function () {
      stops[s].classList.remove("lit");
      s = (s + 1) % stops.length;
      stops[s].classList.add("lit");
    }, 2200);
  } else if (stops.length) {
    stops.forEach(function (st) { st.classList.add("lit"); });
  }

  // Break-even calculator
  var calc = document.querySelector(".calc:not(.mcalc):not(.rcalc):not(.gcalc)");
  if (calc) {
    var num = function (name) { var v = parseFloat(String(calc.querySelector("[name=" + name + "]").value).replace(/[^0-9.]/g, "")); return isNaN(v) ? 0 : v; };
    var fmt = function (n) { return n.toLocaleString("en-US", { maximumFractionDigits: 1 }); };
    var update = function () {
      var plan = num("plan"), ticket = num("ticket"), margin = num("margin") / 100, job = num("job"), lead = num("lead");
      var perCall = ticket * margin, perJob = job * margin;
      calc.querySelector("[data-out=calls]").textContent = perCall > 0 ? fmt(Math.ceil(plan / perCall)) : "–";
      calc.querySelector("[data-out=leads]").textContent = lead > 0 ? fmt(Math.floor(plan / lead)) : "–";
      calc.querySelector("[data-out=jobs]").textContent = perJob > 0 ? fmt(Math.round((plan / perJob) * 10) / 10) : "–";
    };
    calc.addEventListener("input", update);
    update();
  }

  // Review gap calculator
  var rc = document.querySelector(".rcalc");
  if (rc) {
    var rnum = function (name) { var v = parseFloat(String(rc.querySelector("[name=" + name + "]").value).replace(/[^0-9.]/g, "")); return isNaN(v) ? 0 : v; };
    var rupdate = function () {
      var mine = rnum("jobs") * rnum("rate") / 100, gap = rnum("them") - rnum("you"), pace = mine - rnum("their");
      rc.querySelector("[data-out=mine]").textContent = (Math.round(mine * 10) / 10).toLocaleString("en-US");
      rc.querySelector("[data-out=months]").textContent = gap <= 0 ? "Already ahead" : pace <= 0 ? "Never at this pace" : Math.ceil(gap / pace).toLocaleString("en-US");
    };
    rc.addEventListener("input", rupdate);
    rupdate();
  }

  // Missed-call cost calculator
  var mc = document.querySelector(".mcalc");
  if (mc) {
    var mnum = function (name) { var v = parseFloat(String(mc.querySelector("[name=" + name + "]").value).replace(/[^0-9.]/g, "")); return isNaN(v) ? 0 : v; };
    var usd = function (n) { return "$" + Math.round(n).toLocaleString("en-US"); };
    var mupdate = function () {
      var week = mnum("calls") * mnum("job") * mnum("close") / 100;
      mc.querySelector("[data-out=week]").textContent = usd(week);
      mc.querySelector("[data-out=month]").textContent = usd(week * 52 / 12);
      mc.querySelector("[data-out=year]").textContent = usd(week * 52);
    };
    mc.addEventListener("input", mupdate);
    mupdate();
  }

  // Pricing: monthly / annual toggle
  document.querySelectorAll(".pricing").forEach(function (box) {
    var set = function (mode) {
      box.setAttribute("data-billing", mode);
      box.querySelectorAll("[data-bill]").forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.bill === mode ? "true" : "false"); });
      box.querySelectorAll("[data-monthly]").forEach(function (el) { el.textContent = el.getAttribute("data-" + mode); });
    };
    box.querySelectorAll("[data-bill]").forEach(function (b) { b.addEventListener("click", function () { set(b.dataset.bill); }); });
  });

  // Website boxes (hero, closing CTA) start the report card with the site filled in
  document.querySelectorAll("[data-url-form]").forEach(function (f) {
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      var target = document.querySelector("#report-card .rc-form");
      var v = f.querySelector("input").value.trim();
      if (!target) return;
      var site = target.querySelector("[name=website]");
      if (v) {
        site.value = /^https?:\/\//i.test(v) ? v : "https://" + v;
        if (target._go) target._go(1);
      }
      document.getElementById("report-card").scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth" });
      setTimeout(function () { var i = target.querySelector(".rc-step.on input"); if (i) i.focus({ preventScroll: true }); }, 500);
    });
  });

  // Report card form: four steps, posts to /api/lead
  var preview = !!document.querySelector("meta[name=site-preview]");
  document.querySelectorAll(".rc-form").forEach(function (form) {
    var stepsEls = form.querySelectorAll(".rc-step");
    var bars = form.querySelectorAll(".rc-progress i");
    var err = form.querySelector(".rc-error");
    var cur = 0;
    var go = function (n) {
      cur = n;
      stepsEls.forEach(function (el, k) { el.classList.toggle("on", k === n); });
      bars.forEach(function (b, k) { b.classList.toggle("on", k <= n); });
      err.textContent = "";
      var f = stepsEls[n].querySelector("input");
      if (f && document.activeElement && form.contains(document.activeElement)) f.focus();
    };
    var valid = function (n) {
      var inputs = stepsEls[n].querySelectorAll("input[required]");
      for (var k = 0; k < inputs.length; k++) {
        if (!inputs[k].checkValidity()) { err.textContent = inputs[k].dataset.msg || "Please fill this in."; inputs[k].focus(); return false; }
      }
      return true;
    };
    form._go = go;
    form.querySelectorAll("[data-next]").forEach(function (b) {
      b.addEventListener("click", function () { if (valid(cur)) go(cur + 1); });
    });
    form.querySelectorAll(".rc-back").forEach(function (b) { b.addEventListener("click", function () { go(Math.max(0, cur - 1)); }); });
    form.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && e.target.tagName === "INPUT" && cur < stepsEls.length - 1) { e.preventDefault(); if (valid(cur)) go(cur + 1); }
    });
    var site = form.querySelector("[name=website]");
    site.addEventListener("blur", function () {
      var v = site.value.trim();
      if (v && !/^https?:\/\//i.test(v)) site.value = "https://" + v;
    });
    var done = function () {
      form.querySelector(".rc-body").style.display = "none";
      form.querySelector(".rc-done").classList.add("on");
    };
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!valid(cur)) return;
      var data = {};
      new FormData(form).forEach(function (v, k) { data[k] = v; });
      data.page = location.pathname;
      var btn = form.querySelector("[type=submit]");
      btn.disabled = true; btn.textContent = "Sending…";
      if (preview) { setTimeout(done, 500); return; }
      fetch("/api/lead", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) })
        .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
        .then(function (res) {
          if (!res.ok) throw new Error(res.j && res.j.error ? res.j.error : "Something went wrong.");
          done();
        })
        .catch(function (ex) {
          err.textContent = ex.message || "Something went wrong. Please try again.";
          btn.disabled = false; btn.textContent = "Send my report card";
          if (window.turnstile) window.turnstile.reset();
        });
    });
  });
})();

// Founder video bubble: open in a dialog, remember if hidden
(function () {
  var box = document.querySelector("[data-fv]");
  if (!box) return;
  var key = "fv-hidden";
  try { if (localStorage.getItem(key) === "1") { box.classList.add("hide"); return; } } catch (e) {}
  var dlg = box.querySelector("dialog");
  var vid = dlg.querySelector("video");
  box.querySelector(".fv-bubble").addEventListener("click", function () {
    if (dlg.showModal) dlg.showModal(); else dlg.setAttribute("open", "");
    if (vid) { var p = vid.play(); if (p && p.catch) p.catch(function () {}); }
  });
  var close = function () { if (vid) vid.pause(); if (dlg.close) dlg.close(); else dlg.removeAttribute("open"); };
  dlg.querySelector(".fv-close").addEventListener("click", close);
  dlg.addEventListener("click", function (e) { if (e.target === dlg) close(); });
  dlg.addEventListener("close", function () { if (vid) vid.pause(); });
  var cta = dlg.querySelector("[data-fv-cta]");
  if (cta) cta.addEventListener("click", close);
  box.querySelector(".fv-x").addEventListener("click", function () {
    box.classList.add("hide");
    try { localStorage.setItem(key, "1"); } catch (e) {}
  });
})();
