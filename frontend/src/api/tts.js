import { api } from "./http";

// Cache each request's promise, so replaying text doesn't call Google again
// and rapid repeat clicks share one request.
const MAX_CACHED_CLIPS = 100;
const cache = new Map();

export function synthesizeSpeech(text, language) {
  const key = `${language}\n${text}`;
  const cached = cache.get(key);
  if (cached) {
    // Re-insert so the Map's insertion order tracks recency of use.
    cache.delete(key);
    cache.set(key, cached);
    return cached;
  }
  const request = api("/api/tts", { method: "POST", body: { text, language } });
  cache.set(key, request);
  // Don't cache failures, or every replay would fail.
  request.catch(() => {
    if (cache.get(key) === request) cache.delete(key);
  });
  if (cache.size > MAX_CACHED_CLIPS) {
    cache.delete(cache.keys().next().value);
  }
  return request;
}
