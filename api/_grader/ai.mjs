// The AI's four jobs. None of them sets a score.
// Needs ANTHROPIC_API_KEY. Model from GRADER_MODEL (default claude-opus-5-5).
import { nameMatches } from './names.mjs';
import { STATES } from './trades/region.mjs';

const MODEL = process.env.GRADER_MODEL || 'claude-opus-5-5';
let client;

async function getClient() {
  if (!client) {
    const { default: Anthropic } = await import('@anthropic-ai/sdk');
    client = new Anthropic();
  }
  return client;
}

async function ask(params) {
  const c = await getClient();
  const res = await c.beta.messages.create({
    model: MODEL,
    max_tokens: 2000,
    output_config: { effort: 'low' },
    betas: ['server-side-fallback-2026-07-01'],
    fallbacks: 'default',
    ...params,
  });
  return res;
}

const textOf = (res) => (res.stop_reason === 'refusal' ? '' : res.content.filter((b) => b.type === 'text').map((b) => b.text).join('').trim());

// 1. Title, description and main heading: clear, vague or wrong.
export async function titleVerdict({ title, metaDescription, h1 }, trade) {
  const res = await ask({
    system: `You check whether a business website's title says what the business does and where. Reply with exactly one word: clear, vague or wrong.
clear = it says the business offers ${trade.titleWhat} and names a town or area.
vague = it is about the right kind of business but leaves out what or where.
wrong = it describes a different kind of business.`,
    messages: [{ role: 'user', content: `Title: ${title || '(none)'}\nDescription: ${metaDescription || '(none)'}\nMain heading: ${h1 || '(none)'}` }],
  });
  const word = textOf(res).toLowerCase().match(/\b(clear|vague|wrong)\b/);
  return word ? word[1] : null;
}

// 2. What the visible reviews praise and complain about. Plain words only.
export async function reviewThemes(reviews) {
  if (!reviews?.length) return null;
  const res = await ask({
    system: 'Read these customer reviews of a home service company. Reply with two lines and nothing else:\npraise: <a short phrase, at most eight words>\ncomplaint: <a short phrase, at most eight words, or none>',
    messages: [{ role: 'user', content: reviews.map((r, i) => `Review ${i + 1} (${r.rating} stars): ${r.text}`).join('\n\n') }],
  });
  const t = textOf(res);
  const clean = (s) => (s || '').replace(/[^A-Za-z0-9 ,'-]/g, '').trim().slice(0, 80) || null;
  const praise = clean(t.match(/praise:\s*(.+)/i)?.[1]);
  const complaint = clean(t.match(/complaint:\s*(.+)/i)?.[1]);
  return { praise, complaint: /^none$/i.test(complaint || '') ? null : complaint };
}

// 3. Directory searches. We read the result links ourselves; the AI's prose is ignored.
export async function directorySearch({ businessName, town, state }, trade) {
  const domains = trade.directories.map((d) => d.domain);
  const messages = [{
    role: 'user',
    content: `Find the listings for the ${trade.noun} "${businessName}" in ${[town, STATES[state]].filter(Boolean).join(', ') || 'the United States'} on these sites: ${trade.directories.map((d) => d.name).join(', ')}. Run up to three searches. Just search; no summary needed.`,
  }];
  const results = [];
  for (let turn = 0; turn < 3; turn++) {
    const res = await ask({
      messages,
      tools: [{ type: 'web_search_20260209', name: 'web_search', max_uses: 3, allowed_domains: domains }],
    });
    for (const b of res.content) {
      if (b.type === 'web_search_tool_result' && Array.isArray(b.content)) {
        for (const r of b.content) if (r.type === 'web_search_result') results.push({ url: r.url, title: r.title });
      }
    }
    if (res.stop_reason !== 'pause_turn') break;
    messages.push({ role: 'assistant', content: res.content });
  }
  const found = new Set();
  for (const r of results) {
    const dir = trade.directories.find((d) => { try { return new URL(r.url).hostname.endsWith(d.domain); } catch { return false; } });
    if (dir && (nameMatches(r.title, businessName, trade, town) || nameMatches(decodeURIComponent(new URL(r.url).pathname), businessName, trade, town))) found.add(dir.name);
  }
  return { found: [...found], checked: trade.directories.map((d) => d.name), resultCount: results.length, model: MODEL };
}

// 4. Opening paragraph, written from the finished grades only.
export async function openingParagraph(report, businessName) {
  const areaNames = { profile: 'Google profile', reviews: 'Reviews', website: 'Website', listings: 'Listings' };
  const facts = Object.entries(report.areas)
    .filter(([, a]) => a.score != null)
    .map(([k, a]) => `${areaNames[k]}: ${a.grade} (${a.score})${a.topFix ? `. Top fix: ${a.topFix}` : ''}`).join('\n');
  const res = await ask({
    system: `Write a three-sentence opening paragraph for a report card on a local home service business's online presence. Use only the facts given. Sentence one: the overall grade and what is working. Sentence two: the top fix for the lowest-scoring area. Sentence three: a plain, low-pressure note on what fixing it would mean for calls. Never call an area scoring 80 or more a problem. No links, addresses, phone numbers, prices or promises of rankings. Plain words, no exclamation marks.`,
    messages: [{ role: 'user', content: `Business: ${businessName}\nOverall: ${report.grade} (${report.overall})\nLowest area: ${areaNames[report.weakest]}\n${facts}` }],
  });
  const p = textOf(res);
  // Dropped if it contains anything that looks like a link, address or phone number.
  if (!p || /https?:|www\.|\.com\b|\d{3}[\s.-]\d{4}|\b\d{2,5}\s+\w+\s+(st|street|rd|road|ave|avenue|dr|drive|blvd|hwy|lane|ln)\b/i.test(p)) return null;
  return p;
}
