// HVAC grading rules. Every number here is in hvac-rubric.md; change both together.
export default {
  id: 'hvac',
  label: 'HVAC',
  noun: 'HVAC company',
  criteriaVersion: 'hvac-1 (11 Oct 2026)',

  // Local search. Each query is scored and the scores averaged.
  // The first query also supplies the competitors for the reviews comparison.
  searchQueries: ['HVAC near {town}, {state}'],
  areaQuery: 'HVAC',
  areaMiles: 30, // keep in step with AREA_MILES in report.mjs

  // Google's main category. Matched against Places' primaryType and its display name.
  categories: {
    typeIds: ['hvac_contractor', 'air_conditioning_contractor', 'heating_contractor',
      'air_conditioning_repair_service', 'furnace_repair_service'],
    names: ['hvac contractor', 'air conditioning contractor', 'heating contractor',
      'air conditioning repair service', 'furnace repair service',
      'air conditioning system supplier', 'heating equipment supplier'],
  },

  reviews: {
    ratingTiers: [[4.8, 35], [4.6, 32], [4.4, 29], [4.0, 25], [3.7, 19], [3.3, 12], [0, 6]],
    countTiers: [[500, 30], [250, 27], [120, 23], [60, 19], [30, 15], [15, 10], [5, 5], [0, 0]],
    recencyTiers: [[14, 15], [30, 13], [90, 10], [180, 7], [Infinity, 4]],
  },

  // Words that describe the trade, not the business. Removed before directory matching
  // and used by the fallback title check.
  tradeWords: ['hvac', 'heating', 'air', 'cooling', 'conditioning', 'ac', 'a/c', 'heat',
    'refrigeration', 'mechanical', 'comfort', 'climate', 'furnace'],

  // Service pages: each group counts once if any pattern matches a home-page link.
  servicePages: {
    'AC repair': /\b(ac|a\/c|air[- ]?condition\w*|cooling)[- ]?(repair|service)/i,
    'heating': /\b(heat(ing)?|furnace)\b/i,
    'installation': /\b(install\w*|replace\w*|new[- ]system)/i,
    'maintenance plan': /\b(maintenance|tune[- ]?up|membership|club|agreement)/i,
    'heat pump': /heat[- ]?pump/i,
    'ductwork': /\bduct/i,
    'indoor air quality': /(air[- ]?quality|iaq|purif|humidif|filtration)/i,
    'commercial': /\bcommercial\b/i,
  },

  // Texas ACR contractor license; only checked for Texas shops (licenseState), e.g. "TACLA00012345C" or "TACLA 12345E".
  licensePattern: /\bTACLA\s?#?\s?\d{4,8}[CE]?\b/i,
  licenseName: 'TACLA license number',
  licenseState: 'TX',

  directories: [
    { name: 'Facebook', domain: 'facebook.com' },
    { name: 'Yelp', domain: 'yelp.com' },
    { name: 'BBB', domain: 'bbb.org' },
    { name: 'Angi', domain: 'angi.com' },
    { name: 'Nextdoor', domain: 'nextdoor.com' },
    { name: 'Thumbtack', domain: 'thumbtack.com' },
    { name: 'HomeAdvisor', domain: 'homeadvisor.com' },
  ],

  // Title check wording for the AI and for the fallback rule.
  titleWhat: 'heating and air conditioning (HVAC) service',
};
