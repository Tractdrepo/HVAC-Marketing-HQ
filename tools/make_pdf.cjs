// Prints the free downloads to PDF. Run from site/ with a local server on 8765:
//   python3 -m http.server 8765 & node tools/make_pdf.cjs
const { chromium } = require(process.env.PW || "playwright");
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto("http://localhost:" + (process.env.PORT || 8765) + "/downloads/hvac-online-scorecard-print.html", { waitUntil: "networkidle" });
  await p.pdf({ path: "downloads/hvac-online-scorecard.pdf", format: "Letter", printBackground: true });
  await b.close();
})();
