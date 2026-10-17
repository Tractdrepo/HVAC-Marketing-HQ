// Name matching for directory results. A result counts when its title or address carries
// the business's own name words, not town or trade words.

const FILLER = ['llc', 'inc', 'co', 'company', 'corp', 'the', 'and', 'of', 'services', 'service',
  'solutions', 'pros', 'experts', 'specialists', 'contractors', 'contractor',
  'central', 'home', 'residential', 'commercial'];

const norm = (s) => (s || '').toLowerCase().replace(/&/g, ' and ').replace(/[^a-z0-9]+/g, ' ').trim();

export function nameWords(businessName, trade, town) {
  const townWords = new Set(norm(town).split(' ').filter(Boolean));
  const stop = new Set([...FILLER, ...trade.tradeWords.map(norm)]);
  return norm(businessName).split(' ').filter((w) => w && !stop.has(w) && !townWords.has(w));
}

// slugMin: shortest name word allowed to match inside run-together text like a domain. Short words
// hide inside longer ones ("pro" in "airproshvac"), so the Google profile lookup asks for 4.
export function nameMatches(haystack, businessName, trade, town, { slugMin = 1 } = {}) {
  const h = ` ${norm(haystack)} `;
  const slug = (haystack || '').toLowerCase().replace(/[^a-z0-9]/g, '');
  const words = nameWords(businessName, trade, town);
  if (!words.length) {
    // Nothing distinctive left (e.g. "Waco Heating and Air"): the whole name must appear.
    const phrase = norm(businessName);
    return h.includes(` ${phrase} `) || slug.includes(phrase.replace(/ /g, ''));
  }
  return words.every((w) => h.includes(` ${w} `) || (w.length >= slugMin && slug.includes(w)));
}
