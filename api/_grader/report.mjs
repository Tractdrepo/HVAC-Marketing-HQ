// Turns a graded result into the report card email and the link to the personal results page.
// Shows grades, scores out of 100, what we saw and the top fix. The rubric's point values stay internal.
import { grade } from './grade.mjs';

export const AREAS = [
  ['profile', 'Google profile'],
  ['reviews', 'Reviews'],
  ['website', 'Website'],
  ['listings', 'Listings'],
];

const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const known = (v) => v !== null && v !== undefined;
const pct = (v) => (known(v) ? Math.round(v * 100) : null);
const lc = (n) => n.replace(/^(Reviews|Website|Listings)$/, (m) => m.toLowerCase());
const list = (a) => (a.length <= 1 ? a.join('') : `${a.slice(0, -1).join(', ')} and ${a[a.length - 1]}`);

// Refuse anything that is not a plain public hostname, so the fetcher can't be pointed
// at internal addresses.
export function isPublicSite(raw) {
  if (!raw || raw.length > 200) return false;
  let u;
  try { u = new URL(/^https?:\/\//i.test(raw) ? raw : `https://${raw}`); } catch { return false; }
  if (!/^https?:$/.test(u.protocol) || u.username || u.password || u.port) return false;
  const h = u.hostname.toLowerCase();
  if (!h.includes('.') || /^[\d.]+$/.test(h) || h.includes(':')) return false;
  if (/(^|\.)(localhost|local|internal|lan|home\.arpa)$/.test(h)) return false;
  return true;
}

function ordinal(n) {
  const v = n % 100;
  const s = ['th', 'st', 'nd', 'rd'];
  return n + (s[(v - 20) % 10] || s[v] || s[0]);
}

// One plain line of what we saw in each area.
export function sawLine(key, facts, area) {
  const p = facts.profile;
  const r = facts.reviews;
  const w = facts.website;
  const l = facts.listings;
  if (key === 'profile') {
    if (!p || p.found === false) return 'We could not find a Google profile for this business name and website.';
    const bits = [];
    const s = (p.searches || []).filter((x) => known(x.rank)).sort((a, b) => (b.rank || 99) - (a.rank || 99))[0];
    if (s) bits.push(s.rank ? `${ordinal(s.rank)} of ${s.marketSize} in a search for "${s.query}"` : `not in the first ${s.marketSize} in a search for "${s.query}"`);
    if (p.photos) bits.push(`${p.photos.count} photos${known(p.photos.byBusiness) ? ` (${p.photos.byBusiness} yours)` : ''}`);
    bits.push(p.hasHours ? 'hours listed' : 'no hours listed');
    if (p.primaryCategory) bits.push(`category "${String(p.primaryCategory.name || p.primaryCategory.id).replace(/_/g, ' ')}"`);
    return `${p.name}: ${bits.join(', ')}.`;
  }
  if (key === 'reviews') {
    if (!r || !known(r.count)) return 'We could not see your Google reviews.';
    if (r.count === 0) return 'No Google reviews yet.';
    const c = r.competitors;
    let t = `${r.rating?.toFixed(1)} stars from ${r.count} reviews`;
    if (c) t += `; ${c.n === 1 ? 'the top shop in your search has' : `the ${c.n} shops near the top of your search average`} ${c.avgRating?.toFixed(1)} from ${Math.round(c.avgCount)}`;
    if (known(r.newestDays)) t += `; newest review ${r.newestDays === 0 ? 'today' : `${r.newestDays} days ago`}`;
    t += '.';
    if (r.themes?.praise) t += ` Customers praise ${r.themes.praise}${r.themes.complaint ? `; the complaint that comes up is ${r.themes.complaint}` : ''}.`;
    return t;
  }
  if (key === 'website') {
    if (!w || !w.fetched) return 'We could not load your home page.';
    const bits = [`${w.pageCount} pages linked from the home page`];
    if (known(w.performance)) bits.push(`phone speed ${pct(w.performance)}`);
    if (known(w.lighthouse?.seo)) bits.push(`search basics ${pct(w.lighthouse.seo)}`);
    if (known(w.lighthouse?.accessibility)) bits.push(`accessibility ${pct(w.lighthouse.accessibility)}`);
    bits.push(w.booking ? 'booking link found' : 'no booking link found');
    bits.push(w.chat ? 'chat found' : 'no chat found');
    return `${bits.join(', ')}.`;
  }
  if (key === 'listings') {
    if (!l) return 'We could not check your listings.';
    const bits = [];
    if (Array.isArray(l.directoriesFound)) {
      const missing = (l.directoriesChecked || []).filter((d) => !l.directoriesFound.includes(d));
      bits.push(l.directoriesFound.length ? `A web search found you on ${list(l.directoriesFound)}` : 'A web search did not find you on the main directories');
      if (missing.length && l.directoriesFound.length) bits.push(`not on ${list(missing.slice(0, 3))}`);
    }
    if (l.phoneMatch === true) bits.push('Google phone matches the website');
    if (l.phoneMatch === false) bits.push('Google phone does not match the website');
    if (!bits.length) return area?.score == null ? 'We need your Google profile to check your listings.' : 'Checked your phone and links.';
    return `${bits.join(', ')}.`;
  }
  return '';
}

// Every fix for an area, biggest gap first.
export function fixesFor(area) {
  const fixes = (area.lines || [])
    .filter((l) => l.measured && l.points < l.max && l.fix)
    .sort((a, b) => (b.max - b.points) - (a.max - a.points))
    .map((l) => l.fix);
  if (area.topFix && !fixes.includes(area.topFix)) fixes.unshift(area.topFix);
  return [...(area.notes || []), ...fixes];
}

// A short summary when the AI paragraph isn't available.
export function plainSummary({ facts, report }) {
  const names = Object.fromEntries(AREAS);
  const graded = AREAS.filter(([k]) => known(report.areas[k]?.score));
  const best = graded.slice().sort((a, b) => report.areas[b[0]].score - report.areas[a[0]].score)[0];
  const weak = report.weakest ? report.areas[report.weakest] : null;
  const parts = [`${facts.businessName} scores ${report.overall} overall, ${/^[AEF]/.test(report.grade) ? 'an' : 'a'} ${report.grade}.`];
  if (best && report.areas[best[0]].score >= 80) parts.push(`Your strongest area is ${lc(names[best[0]])} at ${report.areas[best[0]].score}.`);
  if (weak && weak.score < 80) parts.push(`Your ${lc(names[report.weakest])} is the weak spot at ${weak.score}${weak.topFix ? `. Start here: ${weak.topFix.replace(/\.$/, '')}` : ''}.`);
  const missing = AREAS.filter(([k]) => !known(report.areas[k]?.score)).map(([, n]) => lc(n));
  if (missing.length) parts.push(`We could not measure your ${list(missing)}, so ${missing.length > 1 ? 'they are' : 'it is'} left out of the grade.`);
  return parts.join(' ');
}

const color = (g) => (!g ? '#64748b' : g.startsWith('A') ? '#15803d' : g.startsWith('B') ? '#1d4ed8' : g.startsWith('C') ? '#b45309' : '#b91c1c');

// The compact payload the results page reads from its link. Only what the page shows.
export function payload(result, firstName) {
  const { facts, report } = result;
  return {
    v: 1,
    n: facts.businessName,
    w: [facts.town, facts.state].filter(Boolean).join(', '),
    f: firstName || '',
    o: report.overall,
    g: report.grade,
    lo: report.weakest,
    s: report.opening || plainSummary(result),
    d: new Date().toISOString().slice(0, 10),
    a: AREAS.map(([k]) => {
      const a = report.areas[k] || {};
      return { k, g: a.grade || null, s: a.score ?? null, saw: sawLine(k, facts, a), fx: fixesFor(a).slice(0, 4) };
    }),
  };
}

export function resultsUrl(siteUrl, data) {
  return `${siteUrl}/your-report#r=${Buffer.from(JSON.stringify(data)).toString('base64url')}`;
}

export function renderReport(result, { firstName, bookingUrl, siteUrl }) {
  const data = payload(result, firstName);
  const link = resultsUrl(siteUrl, data);
  const names = Object.fromEntries(AREAS);
  const font = 'font-family:Arial,Helvetica,sans-serif';
  // Written like a note from Logan, not a newsletter: no banner, no button, no footer, two links.
  // Designed, image-like emails with buttons are what Gmail files under Promotions.
  const p = (inner, extra = '') => `<p style="${font};font-size:15px;line-height:1.6;color:#111827;margin:0 0 14px;${extra}">${inner}</p>`;
  const rows = data.a.map((a) => {
    const top = a.fx[0];
    const score = known(a.s) ? ` (${a.s} / 100)` : '';
    return `<tr><td style="padding:10px 12px 10px 0;vertical-align:top;${font};font-size:18px;font-weight:700;color:${color(a.g)};width:44px">${esc(a.g || 'N/A')}</td>
<td style="padding:10px 0;vertical-align:top;${font};font-size:15px;line-height:1.5;color:#111827"><b>${esc(names[a.k])}</b>${score}<br>${esc(a.saw)}${top ? `<br>Top fix: ${esc(top)}` : ''}</td></tr>`;
  }).join('');
  const weakName = data.lo ? lc(names[data.lo]) : null;
  const when = new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
  const html = `<!doctype html><html><body style="margin:0;padding:0">
<div style="max-width:600px;padding:8px 4px">
${p(`Hi ${esc(data.f || 'there')},`)}
${p(`Here's the report card for ${esc(data.n)}${data.w ? ` in ${esc(data.w)}` : ''}. Overall you got <b>${esc(data.g || 'N/A')}</b>${known(data.o) ? `, ${data.o} out of 100` : ''}.`)}
${p(esc(data.s.startsWith(`${data.n} scores `) ? data.s.replace(/^.*?\.\s+/, '') : data.s))}
<table role="presentation" style="border-collapse:collapse;margin:0 0 14px">${rows}</table>
${p(`${weakName ? `The one I'd fix first is your ${esc(weakName)}. ` : ''}Your full report, with how each fix works, is here: <a href="${esc(link)}">your full report card</a>.`)}
${p(`If you'd like to walk through it together, you can <a href="${esc(bookingUrl)}">grab 15 minutes on my calendar</a>. Or just reply to this email with a question. It comes straight to me.`)}
${p('Logan<br>HVAC Marketing HQ', 'margin-top:20px')}
${p(`We checked your Google profile, reviews, home page and listings on ${esc(when)}. Anything we couldn't measure is left out of your grade, not counted against you.`, 'font-size:13px;color:#6b7280')}
</div></body></html>`;
  const text = [`Hi ${data.f || 'there'},`, '', `HVAC report card: ${data.n}${data.w ? ` (${data.w})` : ''}`,
    `Overall: ${data.g || 'N/A'}${known(data.o) ? ` (${data.o} / 100)` : ''}`, '', data.s, '',
    ...data.a.flatMap((a) => [`${names[a.k]}: ${a.g || 'N/A'}${known(a.s) ? ` (${a.s} / 100)` : ''}`, `  ${a.saw}`, ...(a.fx[0] ? [`  Top fix: ${a.fx[0]}`] : []), '']),
    `Full report and how to fix it: ${link}`, `Grab 15 minutes on my calendar: ${bookingUrl}`, '', 'Logan', 'HVAC Marketing HQ'].join('\n');
  const article = (g) => (/^[AEF]/.test(g) ? 'an' : 'a');
  return { subject: `Your report card: ${data.n} gets ${data.g ? `${article(data.g)} ${data.g}` : 'graded'}`, html, text, link, data };
}

// A short internal note for the team: what ran and what didn't.
export function teamNote(result, lead, ms) {
  const f = result.facts;
  return [`Report card sent to ${lead.first_name} <${lead.email}> for ${f.businessName} (${lead.website}).`,
    `Grade ${result.report.grade} (${result.report.overall}). Town used: ${[f.town, f.state].filter(Boolean).join(', ') || 'none'}. AI: ${f.ai ? 'on' : 'off'}. Took ${Math.round(ms / 1000)}s.`,
    f.notes.length ? `Notes:\n- ${f.notes.join('\n- ')}` : 'Notes: none, everything measured.'].join('\n');
}

// Grade with a hard deadline so the function never runs past its time limit.
export async function gradeWithDeadline(input, ms, env = process.env) {
  let timer;
  const deadline = new Promise((_, reject) => { timer = setTimeout(() => reject(new Error(`timed out after ${ms / 1000}s`)), ms); });
  try {
    return await Promise.race([grade(input, env), deadline]);
  } finally {
    clearTimeout(timer);
  }
}
