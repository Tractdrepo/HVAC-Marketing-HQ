// Spec-driven calculators (.gcalc). Inputs are only parsed to numbers; the
// formulas come from the page's own JSON spec, never from what a visitor types.
(function () {
  "use strict";
  function num(v) {
    var n = parseFloat(String(v).replace(/[$,\s%]/g, ""));
    return isNaN(n) ? 0 : n;
  }
  function withCommas(n, digits) {
    return n.toLocaleString("en-US", { minimumFractionDigits: digits, maximumFractionDigits: digits });
  }
  function fmt(n, kind) {
    if (typeof n !== "number" || !isFinite(n)) return "–";
    if (kind === "money") return (n < 0 ? "-$" : "$") + withCommas(Math.round(Math.abs(n)), 0);
    if (kind === "int") return withCommas(Math.round(n), 0);
    if (kind === "pct") return withCommas(Math.round(n * 10) / 10, 1) + "%";
    return withCommas(Math.round(n * 10) / 10, 1);
  }
  function setup(box) {
    var el = box.querySelector("script.gcalc-spec");
    if (!el) return;
    var spec;
    try { spec = JSON.parse(el.textContent); } catch (e) { return; }
    var names = spec.fields.slice();
    var outs = spec.outputs.map(function (o) {
      var fn = null;
      try { fn = new Function(names.join(","), '"use strict"; return (' + o.expr + ");"); } catch (e) { fn = null; }
      var params = names.slice();
      names.push(o.id);
      return { id: o.id, fmt: o.fmt, fn: fn, params: params, node: box.querySelector('[data-out="' + o.id + '"]') };
    });
    var update = function () {
      var vals = spec.fields.map(function (id) {
        var input = box.querySelector('[name="' + id + '"]');
        return input ? num(input.value) : 0;
      });
      outs.forEach(function (o) {
        var r = NaN;
        if (o.fn) { try { r = o.fn.apply(null, vals); } catch (e) { r = NaN; } }
        vals.push(r);
        if (o.node) o.node.textContent = fmt(r, o.fmt);
      });
    };
    box.addEventListener("input", update);
    box.addEventListener("change", update);
    update();
  }
  function init() { document.querySelectorAll(".gcalc").forEach(setup); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
