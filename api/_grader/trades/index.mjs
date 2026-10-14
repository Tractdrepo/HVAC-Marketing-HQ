import hvac from './hvac.mjs';

const TRADES = { hvac };

export function getTrade(id = 'hvac') {
  const trade = TRADES[String(id).toLowerCase()];
  if (!trade) throw new Error(`Unknown trade "${id}". Known: ${Object.keys(TRADES).join(', ')}`);
  return trade;
}

export const tradeIds = Object.keys(TRADES);
