// Turns a graded result into the report card email. Shows grades and fixes only;
// the point values and rubric stay internal.
import { grade } from './grade.mjs';

const AREAS = [
  ['profile', 'Google profile'],
  ['reviews', 'Reviews'],
  ['website', 'Website'],
  ['listings', 'Listings'],
];

const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

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

// Fixes to show for an area: every measured line that lost points and has a fix, biggest gap first.
function fixesFor(area) {
  return (area.lines || [])
    .filter((l) => l.measured && l.points < l.max && l.fix)
    .sort((a, b) => (b.max - b.points) - (a.max - a.points))
    .map((l) => l.fix);
}

const color = (g) => (!g ? '#64748b' : g.startsWith('A') ? '#15803d' : g.startsWith('B') ? '#2563eb' : g.startsWith('C') ? '#b45309' : '#b91c1c');

export function renderReport({ facts, report }, { firstName, bookingUrl, siteUrl }) {
  const name = facts.businessName;
  const where = [facts.town, facts.state].filter(Boolean).join(', ');
  const rows = AREAS.map(([k, label]) => {
    const a = report.areas[k] || {};
    const g = a.grade || 'N/A';
    const fixes = fixesFor(a).slice(0, 3);
    const note = a.notFound ? 'We could not find a Google profile for this business name and website.'
      : a.score == null ? 'We could not measure this one.' : '';
    return `<tr><td style="padding:16px 0;border-top:1px solid #e2e8f0;vertical-align:top;width:64px">
  <div style="font:700 28px/1 Arial,sans-serif;color:${color(a.grade)}">${esc(g)}</div></td>
  <td style="padding:16px 0 16px 12px;border-top:1px solid #e2e8f0;font:15px/1.5 Arial,sans-serif;color:#0f172a">
  <b>${esc(label)}</b>${note ? `<br><span style="color:#475569">${esc(note)}</span>` : ''}
  ${fixes.length ? `<ul style="margin:8px 0 0;padding-left:18px;color:#334155">${fixes.map((f) => `<li style="margin:4px 0">${esc(f)}</li>`).join('')}</ul>` : (a.score != null ? '<br><span style="color:#475569">Nothing to fix here. Keep it up.</span>' : '')}
  </td></tr>`;
  }).join('');
  const themes = facts.reviews?.themes;
  const themeLine = themes?.praise ? `<p style="font:15px/1.5 Arial,sans-serif;color:#334155">Your recent reviews praise <b>${esc(themes.praise)}</b>${themes.complaint ? `, and the complaint that comes up is <b>${esc(themes.complaint)}</b>` : ''}.</p>` : '';
  const opening = report.opening ? `<p style="font:16px/1.6 Arial,sans-serif;color:#0f172a">${esc(report.opening)}</p>` : '';
  const html = `<!doctype html><html><body style="margin:0;background:#f1f5f9">
<div style="max-width:600px;margin:0 auto;padding:24px 16px">
<div style="background:#fff;border-radius:12px;padding:28px">
<p style="font:15px/1.5 Arial,sans-serif;color:#334155;margin:0 0 4px">Hi ${esc(firstName || 'there')},</p>
<p style="font:15px/1.5 Arial,sans-serif;color:#334155;margin:0 0 20px">Here's the report card for <b>${esc(name)}</b>${where ? ` in ${esc(where)}` : ''}.</p>
<div style="font:700 13px/1 Arial,sans-serif;letter-spacing:.08em;text-transform:uppercase;color:#64748b">Overall grade</div>
<div style="font:800 56px/1.1 Arial,sans-serif;color:${color(report.grade)};margin:6px 0 16px">${esc(report.grade || 'N/A')}</div>
${opening}
<table role="presentation" style="width:100%;border-collapse:collapse;margin-top:8px">${rows}</table>
${themeLine}
<div style="margin:24px 0 8px;padding:18px;background:#fff7ed;border-radius:10px;font:15px/1.5 Arial,sans-serif;color:#0f172a">
Want help with the fixes? Grab a 15-minute call and we'll walk through this with you. No pitch deck.<br>
<a href="${esc(bookingUrl)}" style="display:inline-block;margin-top:12px;background:#ea580c;color:#fff;text-decoration:none;font-weight:700;padding:12px 18px;border-radius:8px">Book a 15-minute call</a>
</div>
<p style="font:13px/1.5 Arial,sans-serif;color:#64748b;margin-top:20px">We checked your Google profile, reviews, home page and listings on ${esc(new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }))}. Anything we couldn't measure is left out of your grade, not counted against you. Reply to this email with any questions.</p>
</div>
<p style="font:12px/1.5 Arial,sans-serif;color:#94a3b8;text-align:center">HVAC Marketing HQ · <a href="${esc(siteUrl)}" style="color:#94a3b8">hvacmarketinghq.com</a></p>
</div></body></html>`;
  const text = [`Hi ${firstName || 'there'},`, '', `Report card for ${name}${where ? ` in ${where}` : ''}.`, '',
    `Overall grade: ${report.grade || 'N/A'}`, report.opening || '', '',
    ...AREAS.flatMap(([k, label]) => {
      const a = report.areas[k] || {};
      return [`${label}: ${a.grade || 'N/A'}`, ...fixesFor(a).slice(0, 3).map((f) => `  - ${f}`)];
    }), '', `Book a 15-minute call: ${bookingUrl}`].join('\n');
  return { subject: `Your report card: ${name} gets ${report.grade ? `${/^[AF]/.test(report.grade) ? 'an' : 'a'} ${report.grade}` : 'graded'}`, html, text };
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
