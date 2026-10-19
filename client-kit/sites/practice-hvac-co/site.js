// Client site JS: keep UTMs/gclid from the landing URL in hidden fields, and send the lead form as JSON.
(function () {
  var keys = ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "gclid"];
  var q = new URLSearchParams(location.search);
  keys.forEach(function (k) {
    var v = q.get(k) || sessionStorage.getItem(k);
    if (q.get(k)) sessionStorage.setItem(k, v);
    document.querySelectorAll('input[name="' + k + '"]').forEach(function (el) { if (v) el.value = v; });
  });
  var form = document.getElementById("lead-form");
  if (!form) return;
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var status = form.querySelector(".form-status");
    var data = {};
    new FormData(form).forEach(function (v, k) { data[k] = v; });
    status.textContent = "Sending...";
    fetch(form.getAttribute("action"), { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) })
      .then(function (r) { return r.json().catch(function () { return { ok: false }; }); })
      .then(function (j) {
        if (j && j.ok) { form.reset(); status.textContent = "Thanks, your request was received. We reply by email."; }
        else { status.textContent = (j && j.error) || "Sorry, that didn't go through. Please try again or call us."; }
      })
      .catch(function () { status.textContent = "Sorry, that didn't go through. Please try again or call us."; });
  });
})();
