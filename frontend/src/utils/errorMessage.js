// Translation and speech share a per-minute limit; past it, say to wait
// rather than give the usual message.
export function errorMessage(err, message) {
  return err?.status === 429 ? "Too many requests. Try again in a minute." : message;
}
