// How fresh the blog is: fetch the blog page the home page links to and find the newest post date.
// parseNewestDate() is pure so it can be tested on saved HTML.

const MONTHS = 'january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec';

export function parseNewestDate(html, now = Date.now()) {
  const dates = [];
  const push = (d) => { const t = Date.parse(d); if (Number.isFinite(t) && t <= now + 86400000 && t > Date.UTC(2005, 0, 1)) dates.push(t); };
  for (const m of html.matchAll(/<time[^>]*datetime=["']([^"']+)["']/gi)) push(m[1]);
  for (const m of html.matchAll(/"datePublished"\s*:\s*"([^"]+)"/gi)) push(m[1]);
  for (const m of html.matchAll(/article:published_time["'][^>]*content=["']([^"']+)["']/gi)) push(m[1]);
  const text = html.replace(/<script[\s\S]*?<\/script>|<style[\s\S]*?<\/style>/gi, ' ').replace(/<[^>]+>/g, ' ');
  for (const m of text.matchAll(new RegExp(`\\b(${MONTHS})\\.? (\\d{1,2}),? (20\\d\\d)\\b`, 'gi'))) push(`${m[1]} ${m[2]}, ${m[3]}`);
  for (const m of text.matchAll(/\b(\d{1,2})\/(\d{1,2})\/(20\d\d)\b/g)) push(`${m[3]}-${m[1].padStart(2, '0')}-${m[2].padStart(2, '0')}`);
  return dates.length ? Math.max(...dates) : null;
}

export async function blogFreshness(url, { timeoutMs = 8000, now = Date.now() } = {}) {
  if (!url) return { found: false };
  try {
    const res = await fetch(url, { redirect: 'follow', signal: AbortSignal.timeout(timeoutMs), headers: { 'user-agent': 'Mozilla/5.0 (compatible; HVACReportCard/1.0)' } });
    if (!res.ok) return { found: true, newestDays: null, error: `HTTP ${res.status}` };
    const newest = parseNewestDate(await res.text(), now);
    return { found: true, newestDays: newest ? Math.max(0, Math.floor((now - newest) / 86400000)) : null };
  } catch (err) {
    return { found: true, newestDays: null, error: err.name === 'TimeoutError' ? 'timeout' : err.message };
  }
}
