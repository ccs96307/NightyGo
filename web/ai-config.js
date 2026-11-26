export const AI_CONFIG_FORMAT = 'nightygo-ai-profile';
export const DEFAULT_AI_CONFIG = Object.freeze({
  format: AI_CONFIG_FORMAT,
  version: 1,
  searchVisits: 128,
  maxSearchTimeMs: 15000,
});

const VISIT_OPTIONS = new Set([32, 128, 512]);
const TIME_OPTIONS = new Set([5000, 15000, 30000]);

export function validateAiConfig(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    throw new Error('AI profile must be a JSON object.');
  }
  if (value.format !== AI_CONFIG_FORMAT || value.version !== 1) {
    throw new Error('Unsupported AI profile format or version.');
  }
  if (!VISIT_OPTIONS.has(value.searchVisits)) {
    throw new Error('searchVisits must be 32, 128, or 512.');
  }
  if (!TIME_OPTIONS.has(value.maxSearchTimeMs)) {
    throw new Error('maxSearchTimeMs must be 5000, 15000, or 30000.');
  }
  return {
    format: AI_CONFIG_FORMAT,
    version: 1,
    searchVisits: value.searchVisits,
    maxSearchTimeMs: value.maxSearchTimeMs,
  };
}

export function parseAiConfig(text) {
  let parsed;
  try {
    parsed = JSON.parse(text);
  } catch {
    throw new Error('AI profile is not valid JSON.');
  }
  return validateAiConfig(parsed);
}
