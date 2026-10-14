// U.S. states, for reading a state out of the town field and for Google's address parts.
export const STATES = {
  AL: 'Alabama', AK: 'Alaska', AZ: 'Arizona', AR: 'Arkansas', CA: 'California', CO: 'Colorado',
  CT: 'Connecticut', DE: 'Delaware', DC: 'District of Columbia', FL: 'Florida', GA: 'Georgia',
  HI: 'Hawaii', ID: 'Idaho', IL: 'Illinois', IN: 'Indiana', IA: 'Iowa', KS: 'Kansas', KY: 'Kentucky',
  LA: 'Louisiana', ME: 'Maine', MD: 'Maryland', MA: 'Massachusetts', MI: 'Michigan', MN: 'Minnesota',
  MS: 'Mississippi', MO: 'Missouri', MT: 'Montana', NE: 'Nebraska', NV: 'Nevada', NH: 'New Hampshire',
  NJ: 'New Jersey', NM: 'New Mexico', NY: 'New York', NC: 'North Carolina', ND: 'North Dakota',
  OH: 'Ohio', OK: 'Oklahoma', OR: 'Oregon', PA: 'Pennsylvania', RI: 'Rhode Island',
  SC: 'South Carolina', SD: 'South Dakota', TN: 'Tennessee', TX: 'Texas', UT: 'Utah', VT: 'Vermont',
  VA: 'Virginia', WA: 'Washington', WV: 'West Virginia', WI: 'Wisconsin', WY: 'Wyoming',
};

// "Waco, TX" or "Waco Texas" -> { town: 'Waco', state: 'TX' }. State is null when not given.
export function splitTown(raw) {
  const s = String(raw || '').trim().replace(/\s+/g, ' ');
  if (!s) return { town: null, state: null };
  // Longest names first, so "West Virginia" wins over "Virginia". A lowercase abbreviation needs a comma.
  const byLength = Object.entries(STATES).sort((a, b) => b[1].length - a[1].length);
  for (const [abbr, name] of byLength) {
    for (const re of [new RegExp(`^(.+?)[,\\s]+${name}\\.?$`, 'i'), new RegExp(`^(.+?)(?:,\\s*|\\s+(?=[A-Z]{2}$))${abbr}\\.?$`, 'i')]) {
      const m = s.match(re);
      if (m) return { town: m[1].trim().replace(/,$/, ''), state: abbr };
    }
  }
  return { town: s.replace(/,$/, ''), state: null };
}
