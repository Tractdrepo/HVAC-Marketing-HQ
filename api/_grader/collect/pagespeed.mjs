// Google PageSpeed Insights, mobile. Key optional (PAGESPEED_API_KEY) but rate-limited without one.
export async function pagespeed(url, key, { timeoutMs = 45000 } = {}) {
  const q = new URLSearchParams({ url, strategy: 'mobile' });
  for (const c of ['performance', 'seo', 'accessibility', 'best-practices']) q.append('category', c);
  if (key) q.set('key', key);
  try {
    const res = await fetch(`https://www.googleapis.com/pagespeedonline/v5/runPagespeed?${q}`, { signal: AbortSignal.timeout(timeoutMs) });
    if (!res.ok) return { performance: null, lighthouse: null, error: `HTTP ${res.status}` };
    const cats = (await res.json()).lighthouseResult?.categories || {};
    const s = (k) => (typeof cats[k]?.score === 'number' ? cats[k].score : null);
    // A test that did not finish is not evidence of a slow site: leave it out.
    return {
      performance: s('performance'),
      lighthouse: { seo: s('seo'), accessibility: s('accessibility'), bestPractices: s('best-practices') },
    };
  } catch (err) {
    return { performance: null, lighthouse: null, error: err.name === 'TimeoutError' ? 'timeout' : err.message };
  }
}
