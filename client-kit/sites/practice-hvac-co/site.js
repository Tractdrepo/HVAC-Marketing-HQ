// Client site JS: keep UTMs/gclid from the landing URL in hidden fields, send the lead form as JSON,
// and fire GA4 key events (generate_lead, click_to_call) only if GA4 is on the page.
(function () {
  var keys = ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "gclid"];
  var q = new URLSearchParams(location.search);
  keys.forEach(function (k) {
    var v = q.get(k) || sessionStorage.getItem(k);
    if (q.get(k)) sessionStorage.setItem(k, v);
    document.querySelectorAll('input[name="' + k + '"]').forEach(function (el) { if (v) el.value = v; });
  });
  var ev = function (name) { if (typeof window.gtag === "function") window.gtag("event", name); };
  document.querySelectorAll('a[href^="tel:"]').forEach(function (a) { a.addEventListener("click", function () { ev("click_to_call"); }); });
  var form = document.getElementById("lead-form");
  if (!form) return;
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var status = form.querySelector(".form-status");
    var data = {};
    new FormData(form).forEach(function (v, k) { data[k] = v; });
    status.textContent = "Sending...";
    var resetCheck = function () { if (window.turnstile && form.querySelector(".cf-turnstile")) window.turnstile.reset(); };
    fetch(form.getAttribute("action"), { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) })
      .then(function (r) { return r.json().catch(function () { return { ok: false }; }); })
      .then(function (j) {
        if (j && j.ok) { form.reset(); resetCheck(); ev("generate_lead"); status.textContent = "Thanks, your request was received. We reply by email."; }
        else { resetCheck(); status.textContent = (j && j.error) || "Sorry, that didn't go through. Please try again or call us."; }
      })
      .catch(function () { resetCheck(); status.textContent = "Sorry, that didn't go through. Please try again or call us."; });
  });
})();
