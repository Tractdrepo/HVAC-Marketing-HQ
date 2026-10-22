// Turns a graded result into the report card email and the link to the personal results page.
// Shows grades, scores out of 100, what we saw and the top fix. The rubric's point values stay internal.
import { deflateRawSync } from 'node:zlib';
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

// Texting (missed-call text-back, review and follow-up texts) waits on carrier (A2P) approval. While it's
// false the report sells text-back as switching on soon, never as live. Flip with TEXTING_LIVE in your-report.js.
export const TEXTING_LIVE = false;
const TEXT_BACK = TEXTING_LIVE
  ? 'every missed call gets a text back within 10 seconds'
  : 'missed-call text-back (a text to every caller you miss, within 10 seconds) is in every plan and goes live in the next couple of weeks';

// The name to greet. Initials ("LT"), a single letter or anything that isn't a name gets "there";
// all-caps or all-lowercase names are put in normal case.
export function greetName(raw) {
  const words = String(raw || '').trim().split(/\s+/).filter(Boolean);
  if (!words.length || words.length > 2 || !words.every((w) => /^[A-Za-z][A-Za-z'.-]+$/.test(w)) || /^[A-Z.]{2,3}$/.test(words[0])) return '';
  return words.map((w) => (w === w.toUpperCase() || w === w.toLowerCase() ? w[0].toUpperCase() + w.slice(1).toLowerCase() : w)).join(' ');
}

// "Prompt, honest service" reads mid-sentence as "prompt, honest service". Leaves "AC" and names alone.
const midSentence = (t) => (/^[A-Z][a-z]/.test(t || '') ? t[0].toLowerCase() + t.slice(1) : t);

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
    for (const s of (p.searches || []).filter((x) => known(x.rank))) {
      bits.push(s.rank ? `${ordinal(s.rank)} in a search for "${s.query}"` : `not in the first ${s.marketSize} in a search for "${s.query}"`);
    }
    if (p.photos) {
      const n = p.photos.capped ? 'at least 10 photos' : `${p.photos.count} photo${p.photos.count === 1 ? '' : 's'}`;
      const shown = Math.min(p.photos.count, 10);
      const own = p.photos.byBusiness;
      bits.push(!known(own) || !shown ? n : own === shown ? `${n}, all posted by you` : `${n}, ${own} of the first ${shown} posted by you`);
    }
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
    if (r.themes?.praise) t += ` Customers praise ${midSentence(r.themes.praise)}${r.themes.complaint ? `; the complaint that comes up is ${midSentence(r.themes.complaint)}` : ''}.`;
    return t;
  }
  if (key === 'website') {
    if (!w || !w.fetched) return 'We could not load your home page.';
    const bits = [`${w.pageCount} pages linked from the home page`];
    if (known(w.performance)) bits.push(`phone speed ${pct(w.performance)}`);
    if (known(w.lighthouse?.seo)) bits.push(`search basics ${pct(w.lighthouse.seo)}`);
    if (known(w.lighthouse?.accessibility)) bits.push(`accessibility ${pct(w.lighthouse.accessibility)}`);
    bits.push(w.bookingKind === 'online' ? 'online booking found' : w.booking ? 'contact form found' : 'no way to book or request service found');
    if ((w.areaPages || []).length) bits.push(`${w.areaPages.length} town page${w.areaPages.length === 1 ? '' : 's'}`);
    if (w.blog) bits.push(!w.blog.found ? 'no blog' : known(w.blog.newestDays) ? `newest blog post ${w.blog.newestDays} days ago` : 'blog found');
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
    else if (area?.couldNotCheck?.includes('directories')) bits.push('We could not check the directories this time');
    if (l.phoneMatch === true) bits.push('Google phone matches the website');
    if (l.phoneMatch === false) bits.push('Google phone does not match the website');
    if (!bits.length) return area?.score == null ? 'We need your Google profile to check your listings.' : 'Checked your phone and links.';
    return `${bits.join(', ')}.`;
  }
  return '';
}

// How we handle each fix, so every problem the shop reads comes with our answer to it.
// Plan names and inclusions match PLANS and ADDONS in tools/build.py; keep them in step.
const SETUP = 'Fixed in our Google profile setup, included in every plan.';
const BUILD = 'Built into every site we make on our HVAC build.';
export const HOW = {
  profile: {
    search: 'Local SEO plus a managed Google profile (Growth and up) is how we move you up the map.',
    photos: 'Text us job photos from your phone. On Growth and up we post them to your profile every week.',
    website: SETUP, category: SETUP, hours: SETUP, details: SETUP, phone: SETUP,
    closed: 'We fix the status with Google in setup, before anything else.',
    posts: 'On Growth and up we post to your profile every week, using the job photos you text us.',
  },
  reviews: {
    rating: 'Every plan sends a review request after each finished job, with a one-tap link to Google.',
    count: 'Every plan sends a review request after each finished job, with a one-tap link to Google.',
    recent: 'Every plan sends a review request after each job, so new reviews keep coming every week.',
    low: 'On Growth and up we reply to every review, so the next customer sees an owner who answers.',
    replies: 'On Growth and up we write and post a reply to every review for you.',
  },
  website: {
    pages: 'Our sites give each service and each town its own page: 12 pages on Growth, 25 on Dominate.',
    booking: 'Every site we build has a book-service button and a short form that lands in your inbox app.',
    speed: 'Our HVAC build is made for phones; our own site scores 99 for speed on Google\'s phone test.',
    lighthouse: BUILD, title: BUILD, mobile: BUILD, call: BUILD,
    emergency: 'We put it on every page of the site we build.', financing: 'We put it on every page of the site we build.',
    license: 'We put it in the footer of every page we build.',
    chat: 'AI web chat (Growth and up) answers questions and books jobs after hours.',
    schema: 'Every site we build includes business details code for Google and AI search.',
    reviewsOnSite: 'Every site we build shows your Google reviews, updated as new ones come in.',
    faq: 'We write answers to the questions your customers ask, the kind AI search quotes.',
    blog: 'Growth includes a new article every month, written and posted for you.',
    placeholder: 'We check every number and link before your site goes live.',
  },
  listings: {
    directories: 'Directory listings are managed on Dominate, or as an add-on to any plan.',
    phone: 'Fixed in setup: one number on Google, your site and every listing.',
    googleLink: SETUP, facebook: 'We link your Facebook page from the site we build.',
  },
};

// Every fix for an area, biggest gap first, each with how we handle it.
export function fixesFor(area, key) {
  const how = (id) => (key && HOW[key]?.[id]) || null;
  const fixes = (area.lines || [])
    .filter((l) => l.measured && l.points < l.max && l.fix)
    .sort((a, b) => (b.max - b.points) - (a.max - a.points))
    .map((l) => ({ t: l.fix, h: how(l.id) }));
  if (area.topFix && !fixes.some((f) => f.t === area.topFix)) fixes.unshift({ t: area.topFix, h: how(area.topFixId) });
  return [...(area.notes || []).map((t) => ({ t, h: how('placeholder') })), ...fixes, ...(area.advice || []).map((a) => ({ t: a.fix, h: how(a.id) }))];
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

const color = (g) => (!g ? '#64748b' : g.startsWith('A') ? '#1d6fd8' : g.startsWith('B') ? '#4f5bd5' : g.startsWith('C') ? '#7c3aed' : '#c2410c');

// The compact payload the results page reads from its link. Only what the page shows.
export function payload(result, firstName) {
  const { facts, report } = result;
  return {
    v: 1,
    n: facts.businessName,
    w: [facts.town, facts.state].filter(Boolean).join(', '),
    f: greetName(firstName),
    o: report.overall,
    g: report.grade,
    lo: report.weakest,
    s: report.opening || plainSummary(result),
    d: new Date().toISOString().slice(0, 10),
    // What the Book and Repeat sections speak to: how a visitor reaches them, and their review flow.
    b: facts.website?.fetched ? { k: facts.website.bookingKind || null, c: Boolean(facts.website.chat), t: Boolean(facts.website.tapToCall) } : null,
    rv: facts.reviews && known(facts.reviews.count) ? { n: facts.reviews.count, d: facts.reviews.newestDays ?? null } : null,
    a: AREAS.map(([k]) => {
      const a = report.areas[k] || {};
      return { k, g: a.grade || null, s: a.score ?? null, saw: sawLine(k, facts, a), fx: fixesFor(a, k).slice(0, 4).map((f) => [f.t, f.h || '']) };
    }),
  };
}

// Compressed (deflate-raw) so the link in the email stays short; the page still reads old #r= links.
export function resultsUrl(siteUrl, data) {
  return `${siteUrl}/your-report#z=${deflateRawSync(Buffer.from(JSON.stringify(data)), { level: 9 }).toString('base64url')}`;
}

export const AREA_MILES = 30;

// Book: what we saw about how a visitor reaches them, then what our plans add. HTML, already escaped.
export function bookLines(data) {
  const b = data.b;
  let saw = 'We could not load your site, so we could not check how customers reach you.';
  if (b) {
    const found = [b.k === 'online' && 'online booking', b.k === 'form' && 'a contact form', b.c && 'a chat tool', b.t && 'a tap-to-call number'].filter(Boolean);
    const missing = [b.k !== 'online' && (b.k === 'form' ? 'online booking' : 'booking form'), !b.c && 'chat', !b.t && 'tap-to-call number'].filter(Boolean);
    const none = list(missing).replace(/ and ([^ ]+[^,]*)$/, ' or $1');
    saw = found.length ? `On your site we found ${list(found)}${missing.length ? `, but no ${none}` : ''}.` : `On your site we found no ${none}.`;
  }
  return [
    `<b>What we saw:</b> ${esc(saw)}`,
    `<b>How we fix it:</b> every site we build has a book-service button and a short form, and calls, texts and web leads land in one inbox your office can see. ${TEXT_BACK[0].toUpperCase()}${TEXT_BACK.slice(1)}. On Growth and up, AI web chat answers and books after hours; AI phone answering is an add-on for the rush.`,
  ];
}

// Repeat: their review flow, then what our plans add.
export function repeatLines(data) {
  const r = data.rv;
  const saw = !r ? 'We could not see your Google reviews.'
    : `${r.n} Google reviews${known(r.d) ? `, the newest ${r.d === 0 ? 'today' : `${r.d} days ago`}` : ''}. The shops that stay on top ask after every job and reply to every review.`;
  return [
    `<b>What we saw:</b> ${esc(saw)}`,
    '<b>How we fix it:</b> every plan sends a review request after each finished job. On Growth and up we reply to every review, follow up on open quotes until they are booked or lost, and reach out to past customers each season for tune-ups. You see it all in your HQ Command Center dashboard.',
  ];
}

export function renderReport(result, { firstName, bookingUrl, siteUrl }) {
  const data = payload(result, firstName);
  const link = resultsUrl(siteUrl, data);
  const names = Object.fromEntries(AREAS);
  const font = 'font-family:Arial,Helvetica,sans-serif';
  // Laid out like the Zero Vacancy report (which lands in Primary): one card, the grade up top, one
  // button. No images, no tracking, and every link on our own domain.
  const rows = data.a.map((a) => {
    const top = a.fx[0];
    const score = known(a.s) ? ` <span style="color:#64748b;font-weight:400">${a.s} / 100</span>` : '';
    return `<tr><td style="padding:16px 0;border-top:1px solid #e5e7eb;vertical-align:top;width:52px;${font};font-weight:700;font-size:22px;line-height:1.1;color:${color(a.g)}">${esc(a.g || 'N/A')}</td>
<td style="padding:16px 0 16px 8px;border-top:1px solid #e5e7eb;${font};font-size:14px;line-height:1.55;color:#111827">
<b>${esc(names[a.k])}</b>${score}<br><span style="font-size:13px;color:#4b5563">${esc(a.saw)}</span>
${top ? `<br><b>Top fix:</b> ${esc(top[0])}` : ''}${top && top[1] ? `<br><span style="color:#c2410c"><b>How we fix it:</b> ${esc(top[1])}</span>` : ''}</td></tr>`;
  }).join('');
  const box = (title, lines) => `<div style="margin-top:18px;padding:16px 18px;background:#f9fafb;border-radius:8px;${font};font-size:13px;line-height:1.6;color:#111827">
<div style="font-size:11px;font-weight:700;letter-spacing:.14em;color:#c2410c;margin-bottom:6px">${title}</div>${lines.map((l) => `<div style="margin-top:6px">${l}</div>`).join('')}</div>`;
  const weakName = data.lo ? lc(names[data.lo]) : null;
  const when = new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
  const summary = data.s.startsWith(`${data.n} scores `) ? data.s.replace(/^.*?\.\s+/, '') : data.s;
  const html = `<!doctype html><html><body style="margin:0;padding:0;background:#f3f4f6">
<div style="max-width:600px;margin:0 auto;padding:24px 12px">
<div style="background:#ffffff;border:1px solid #e5e7eb;border-radius:10px;padding:26px 24px">
<table role="presentation" style="width:100%;border-collapse:collapse"><tr>
<td style="${font};vertical-align:top"><div style="font-size:11px;font-weight:700;letter-spacing:.16em;color:#c2410c">HVAC MARKETING HQ</div>
<div style="font-size:12px;color:#6b7280;margin-top:16px">HVAC report card</div>
<div style="font-size:19px;font-weight:700;color:#111827;line-height:1.3">${esc(data.n)}</div>${data.w ? `<div style="font-size:12px;color:#6b7280">${esc(data.w)}</div>` : ''}</td>
<td style="${font};text-align:right;vertical-align:top;white-space:nowrap"><div style="font-size:40px;font-weight:800;line-height:1;color:${color(data.g)}">${esc(data.g || 'N/A')}</div><div style="font-size:12px;color:#6b7280;margin-top:6px">${known(data.o) ? `${data.o} / 100` : ''}</div></td>
</tr></table>
<p style="${font};font-size:14px;line-height:1.6;color:#111827;margin:18px 0 10px">Hi ${esc(data.f || 'there')},</p>
<p style="${font};font-size:14px;line-height:1.6;color:#111827;margin:0 0 12px">${esc(summary)}</p>
<p style="${font};font-size:14px;line-height:1.6;color:#111827;margin:0 0 16px">Want help with it? <a href="${esc(bookingUrl)}" style="color:#c2410c;font-weight:700">Book a 15-minute walkthrough</a> of this report.</p>
<div style="${font};font-size:11px;font-weight:700;letter-spacing:.14em;color:#c2410c;margin:4px 0 2px">1. RANK: HOW CUSTOMERS FIND YOU</div>
<table role="presentation" style="width:100%;border-collapse:collapse">${rows}</table>
${box('2. BOOK: TURNING VISITS AND CALLS INTO JOBS', bookLines(data))}
${box('3. REPEAT: CUSTOMERS WHO COME BACK AND REVIEW YOU', repeatLines(data))}
<div style="border-top:1px solid #e5e7eb;padding-top:16px;margin-top:20px;${font};font-size:14px;line-height:1.6;color:#111827">
${weakName ? `Your lowest grade is <b>your ${esc(weakName)}</b>. ` : ''}Book 15 minutes and I'll show you how we'd fix it and what it would cost.
<div style="margin:14px 0 4px"><a href="${esc(bookingUrl)}" style="display:inline-block;background:#c2410c;color:#ffffff;text-decoration:none;${font};font-weight:700;font-size:14px;padding:11px 18px;border-radius:7px">Book a 15-minute walkthrough</a></div>
</div>
<p style="${font};font-size:13px;line-height:1.6;color:#4b5563;margin:16px 0 0">Not ready to talk? <a href="${esc(link)}" style="color:#c2410c">See your full report and how each fix works</a>, or just reply to this email with a question. It comes straight to me.</p>
<p style="${font};font-size:13px;line-height:1.6;color:#111827;margin:14px 0 0">Logan<br>HVAC Marketing HQ</p>
<p style="${font};font-size:11px;line-height:1.5;color:#9ca3af;margin:16px 0 0">We checked your Google profile, reviews, home page and listings on ${esc(when)}. Anything we couldn't measure is left out of your grade, not counted against you. Map rankings compare you with HVAC businesses within ${AREA_MILES} miles of your shop.</p>
</div></div></body></html>`;
  const text = [`Hi ${data.f || 'there'},`, '', `HVAC report card: ${data.n}${data.w ? ` (${data.w})` : ''}`,
    `Overall: ${data.g || 'N/A'}${known(data.o) ? ` (${data.o} / 100)` : ''}`, '', data.s, '',
    ...data.a.flatMap((a) => [`${names[a.k]}: ${a.g || 'N/A'}${known(a.s) ? ` (${a.s} / 100)` : ''}`, `  ${a.saw}`, ...(a.fx[0] ? [`  Top fix: ${a.fx[0][0]}`, ...(a.fx[0][1] ? [`  How we fix it: ${a.fx[0][1]}`] : [])] : []), '']),
    `Full report and how to fix it: ${link}`, `Grab 15 minutes on my calendar: ${bookingUrl}`, '', 'Logan', 'HVAC Marketing HQ'].join('\n');
  const article = (g) => (/^[AEF]/.test(g) ? 'an' : 'a');
  // The grade goes in the subject only when it's a B or better; a low letter in the inbox reads as an insult
  // before they've seen why, so those get a neutral subject and the grade inside.
  const subject = /^[AB]/.test(data.g || '') ? `Your report card: ${data.n} gets ${article(data.g)} ${data.g}` : `Your HVAC report card for ${data.n} is ready`;
  return { subject, html, text, link, data };
}

// A short internal note for the team: what ran and what didn't.
export function teamNote(result, lead, ms) {
  const f = result.facts;
  return [`Report card sent to ${lead.first_name} <${lead.email}> for ${f.businessName} (${lead.website}).`,
    `Grade ${result.report.grade} (${result.report.overall}). Town used: ${[f.town, f.state].filter(Boolean).join(', ') || 'none'}. AI: ${f.ai ? 'on' : 'off'}. Took ${Math.round(ms / 1000)}s.`,
    f.notes.length ? `Notes:\n- ${f.notes.join('\n- ')}` : 'Notes: none, everything measured.'].join('\n');
}

// Why a graded result must not go to the shop automatically, or null when it can.
export function holdReason(result) {
  if (result.partial) return `some checks failed, so the grade would be built on missing facts:\n- ${(result.failures || []).join('\n- ')}`;
  if (result.report.overall == null) return `nothing could be measured (${result.facts.notes.join(' ')})`;
  return null;
}

// Team-only: the Google searches tried when no profile was matched, the top candidates each returned,
// and one word for why each was passed over. Plain text, at most ~25 lines. Never goes to the shop.
export const DEBUG_MAX_LINES = 25;
export function lookupDebugText(facts) {
  const trace = facts?.lookupDebug;
  if (!Array.isArray(trace) || !trace.length) return '';
  const cut = (v, n) => { const s = String(v ?? '').replace(/\s+/g, ' ').trim(); return s.length > n ? `${s.slice(0, n - 1)}…` : s; };
  const lines = ['Google lookup debug (team only): no profile matched.'];
  trace.forEach((t, i) => {
    lines.push(`Q${i + 1} "${cut(t.query, 60)}": ${t.error ? 'Places error' : `${t.count} result${t.count === 1 ? '' : 's'}`}`);
    for (const c of t.candidates || []) {
      lines.push(`  - ${cut(c.name, 40) || '?'} | ${cut(c.address, 45) || 'no address'} | ${c.host ? cut(c.host, 35) : 'no site'} | ${c.type || 'no type'} | ${c.reviews ?? 0} rev | SAB ${c.serviceArea == null ? '?' : c.serviceArea ? 'yes' : 'no'} -> ${c.reason}`);
    }
  });
  const shown = lines.length > DEBUG_MAX_LINES ? [...lines.slice(0, DEBUG_MAX_LINES - 1), `(${lines.length - DEBUG_MAX_LINES + 1} more lines cut)`] : lines;
  // Belt and braces: nothing that looks like a key or a keyed URL.
  return shown.join('\n').replace(/([?&](key|api_key|apikey)=)[^&\s|]+/gi, '$1[redacted]').replace(/AIza[0-9A-Za-z_-]{20,}/g, '[redacted]');
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
