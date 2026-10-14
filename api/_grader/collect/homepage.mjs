// Fetch the home page once and pull out the facts the website and listings areas need.
// parseHomepage() is pure so it can be tested on saved HTML.
import { STATES } from '../trades/region.mjs';
import { TOWNS } from '../trades/us-towns.mjs';

const BOOKING_WIDGETS = /(servicetitan|housecallpro|housecall\s?pro|getjobber|jobber\.com|fieldedge|servicefusion|leadconnectorhq|msgsndr|scheduleengine|calendly|book\.servicetitan)/i;
const BOOKING_WORDS = /\b(book|schedule|request)\s+(online|now|service|a\s+service|an?\s+appointment|appointment|your\s+service|a\s+call|estimate)/i;
const CHAT_WIDGETS = /(podium|birdeye|leadconnector[^"']*chat|widgets\.leadconnectorhq|intercom|driftt?\.com|tawk\.to|livechatinc|tidio|zendesk|hubspot[^"']*conversations|smith\.ai|ngagelive|apexchat|gorgias|crisp\.chat|olark|signpost|chatbot|webchat)/i;
const EMERGENCY = /\b(24\/7|24-7|24\s*hours?|24-hour|emergency\s+(service|repair|hvac|ac|plumb|electric)|after[- ]hours)/i;
const FINANCING = /\b(financing|finance\s+options|synchrony|greensky|wells\s*fargo|service\s*finance|goodleap|0%\s*apr|monthly\s+payments)/i;
const PHONE = /(?:\+?1[\s.-]?)?\(?([2-9]\d{2})\)?[\s.-]?(\d{3})[\s.-]?(\d{4})\b/g;

export async function fetchHomepage(url, trade, { timeoutMs = 12000 } = {}) {
  const target = /^https?:\/\//i.test(url) ? url : `https://${url}`;
  try {
    const res = await fetch(target, {
      redirect: 'follow',
      signal: AbortSignal.timeout(timeoutMs),
      headers: { 'user-agent': 'Mozilla/5.0 (compatible; CenTexReportCard/1.0)' },
    });
    if (!res.ok) return { fetched: false, error: `HTTP ${res.status}` };
    const html = await res.text();
    return { ...parseHomepage(html, res.url, trade), fetched: true };
  } catch (err) {
    return { fetched: false, error: err.name === 'TimeoutError' ? 'timeout' : err.message };
  }
}

export function parseHomepage(html, finalUrl, trade) {
  const base = new URL(finalUrl);
  const text = decode(html.replace(/<script[\s\S]*?<\/script>|<style[\s\S]*?<\/style>/gi, ' ').replace(/<[^>]+>/g, ' ')).replace(/\s+/g, ' ');

  const links = [...html.matchAll(/<a\b[^>]*href\s*=\s*["']([^"']+)["'][^>]*>([\s\S]*?)<\/a>/gi)]
    .map(([, href, inner]) => ({ href: href.trim(), text: decode(inner.replace(/<[^>]+>/g, ' ')).replace(/\s+/g, ' ').trim() }));

  const internal = new Set();
  for (const l of links) {
    try {
      const u = new URL(l.href, base);
      if (u.hostname.replace(/^www\./, '') === base.hostname.replace(/^www\./, '') && /^https?:$/.test(u.protocol)) {
        const path = u.pathname.replace(/\/+$/, '') || '/';
        if (path !== '/' && !/\.(jpg|jpeg|png|gif|webp|svg|pdf)$/i.test(path)) internal.add(path.toLowerCase());
      }
    } catch { /* bad href */ }
  }

  const linkBlob = links.map((l) => `${l.href} ${l.text}`);
  const phones = [...new Set([...text.matchAll(PHONE), ...links.filter((l) => /^tel:/i.test(l.href)).map((l) => [...l.href.matchAll(PHONE)][0]).filter(Boolean)]
    .map((m) => `${m[1]}${m[2]}${m[3]}`))];
  // Template numbers: a 555 exchange (555-555-5555, 254-555-0100) or one digit repeated.
  const placeholder = phones.find((p) => /^\d{3}555\d{4}$/.test(p) || /^(\d)\1{9}$/.test(p));

  // Town pages: links under a service-area style folder, or link text like "Waco, TX" or "AC repair in Waco".
  const ABBRS = Object.keys(STATES).join('|');
  const areaPages = new Set();
  for (const l of links) {
    let path = '';
    try { path = new URL(l.href, base).pathname.toLowerCase().replace(/\/+$/, ''); } catch { /* bad href */ }
    const folder = path.match(/\/(?:service-areas?|areas-we-serve|areas-served|areas|locations|cities|communities)\/([a-z0-9-]+)/);
    const named = l.text.match(new RegExp(`^([A-Z][\\w.'-]+(?: [A-Z][\\w.'-]+){0,3}),? (?:${ABBRS})$`))
      || l.text.match(/\b(?:in|near) ([A-Z][\w.'-]+(?: [A-Z][\w.'-]+){0,3})$/);
    if (folder) areaPages.add(folder[1]);
    else if (named) areaPages.add(named[1].toLowerCase());
    else if (/service[- ]?areas?|areas[- ]we[- ]serve|locations/i.test(`${l.href} ${l.text}`)) areaPages.add('service area page');
  }
  // A town named only in "proudly serving Waco" text is not a page; only links count.

  const online = BOOKING_WIDGETS.test(html) || linkBlob.some((b) => BOOKING_WORDS.test(b));
  const formOnPage = /<form[\s\S]{0,6000}?(type=["']?(email|tel)|name=["'][^"']*(email|phone|message))/i.test(html);
  const formLink = links.some((l) => /\b(contact( us)?|request (a )?(quote|estimate|service)|get (a )?(free )?(quote|estimate)|free estimate)\b/i.test(l.text) && isInternal(l.href, base));
  const bookingKind = online ? 'online' : formOnPage || formLink ? 'form' : null;

  // Links to one-level pages, kept so town pages can be matched once we know the state.
  const pageLinks = [];
  for (const l of links) {
    try {
      const u = new URL(l.href, base);
      if (!isInternal(l.href, base)) continue;
      const segs = u.pathname.toLowerCase().split('/').filter(Boolean);
      if (segs.length >= 1 && segs.length <= 2 && l.text && l.text.length < 60) pageLinks.push({ text: l.text, slug: segs[segs.length - 1] });
    } catch { /* bad href */ }
  }
  const blogLink = links.find((l) => isInternal(l.href, base) && (/^(blog|news|articles|tips|our blog|latest news)$/i.test(l.text) || /\/(blog|news|articles)\/?$/i.test(l.href)));

  const facts = {
    finalUrl: base.href,
    https: base.protocol === 'https:',
    title: decode(match(html, /<title[^>]*>([\s\S]*?)<\/title>/i)),
    metaDescription: decode(metaContent(html, 'description')),
    h1: decode((match(html, /<h1\b[^>]*>([\s\S]*?)<\/h1>/i) || '').replace(/<[^>]+>/g, ' ')).replace(/\s+/g, ' ').trim(),
    mobileViewport: /<meta[^>]+name=["']viewport["'][^>]+width\s*=\s*device-width/i.test(html) || /<meta[^>]+content=["'][^"']*width\s*=\s*device-width[^"']*["'][^>]+name=["']viewport/i.test(html),
    pageCount: internal.size,
    // Online booking (a scheduler or "Book now") or, just as good for a homeowner, a contact or quote form.
    booking: bookingKind ? true : false,
    bookingKind,
    chat: CHAT_WIDGETS.test(html),
    emergency: EMERGENCY.test(text),
    financing: FINANCING.test(text) || linkBlob.some((b) => /financ/i.test(b)),
    tapToCall: links.some((l) => /^tel:/i.test(l.href)),
    phones: phones.filter((p) => p !== placeholder),
    placeholderPhone: placeholder ? fmtPhone(placeholder) : null,
    facebookLinked: links.some((l) => /facebook\.com\/(?!sharer|share)/i.test(l.href)),
    areaPages: [...areaPages],
    pageLinks: pageLinks.slice(0, 300),
    blogUrl: blogLink ? new URL(blogLink.href, base).href : null,
  };
  if (trade) Object.assign(facts, tradeFacts(facts, html, text, linkBlob, trade));
  return facts;
}

// Facts that depend on the trade's rules.
export function tradeFacts(facts, html, text, linkBlob, trade) {
  return {
    serviceTopics: Object.entries(trade.servicePages)
      .filter(([, re]) => linkBlob.some((b) => re.test(b)))
      .map(([name]) => name),
    license: trade.licensePattern.test(text),
  };
}

// Fallback title check when there is no AI key: trade word + a town = clear.
export function ruleTitleVerdict(facts, trade, { town, state } = {}) {
  const s = `${facts.title || ''} ${facts.metaDescription || ''} ${facts.h1 || ''}`;
  if (!s.trim()) return 'vague';
  const hasTrade = trade.tradeWords.some((w) => new RegExp(`\\b${w.replace('/', '\\/')}\\b`, 'i').test(s))
    || Object.values(trade.servicePages).some((re) => re.test(s));
  const esc = (t) => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const places = [town, state, STATES[state]].filter(Boolean);
  const hasTown = places.some((t) => new RegExp(`\\b${esc(t)}\\b`, 'i').test(s));
  return hasTrade && hasTown ? 'clear' : 'vague';
}

function isInternal(href, base) {
  try {
    const u = new URL(href, base);
    return /^https?:$/.test(u.protocol) && u.hostname.replace(/^www\./, '') === base.hostname.replace(/^www\./, '');
  } catch { return false; }
}

// Town pages the home page links to, matched against real place names in the shop's state:
// link text like "Coolidge" or "Fairfield HVAC", or a slug like /ac-services-mexia/ or /navarro-county-hvac/.
export function townPages(site, state, trade) {
  const names = new Set((TOWNS[state] || '').split('|').filter(Boolean));
  if (!names.size) return site.areaPages || [];
  const fill = new Set(['hvac', 'ac', 'a', 'c', 'air', 'conditioning', 'heating', 'cooling', 'services', 'service', 'repair', 'and', 'in', 'near', 'tx', 'texas', 'contractor', 'company', 'installation', 'company']);
  for (const w of trade?.tradeWords || []) fill.add(w.toLowerCase());
  const clean = (t) => t.toLowerCase().replace(/[^a-z0-9 -]/g, ' ').split(/[\s-]+/).filter((w) => w && !fill.has(w)).join(' ');
  const found = new Set(site.areaPages || []);
  for (const { text, slug } of site.pageLinks || []) {
    for (const cand of [clean(text), clean(slug)]) {
      if (!cand || cand.split(' ').length > 3) continue;
      if (names.has(cand) || /^[a-z]+( [a-z]+)? county$/.test(cand)) { found.add(cand); break; }
    }
  }
  found.delete('service area page');
  return [...found];
}

function match(s, re) { const m = s.match(re); return m ? m[1].trim() : null; }
function metaContent(html, name) {
  const tag = html.match(new RegExp(`<meta[^>]+name=["']${name}["'][^>]*>`, 'i'));
  return tag ? match(tag[0], /content=["']([^"']*)["']/i) : null;
}
function decode(s) {
  if (!s) return s;
  return s.replace(/&amp;/g, '&').replace(/&#39;|&apos;/g, "'").replace(/&quot;/g, '"')
    .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&nbsp;/g, ' ').replace(/&#(\d+);/g, (_, n) => String.fromCharCode(+n));
}
export function fmtPhone(d) { return `(${d.slice(0, 3)}) ${d.slice(3, 6)}-${d.slice(6)}`; }
