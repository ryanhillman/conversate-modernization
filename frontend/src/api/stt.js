import { api } from "./http";

// Above the backend's Google timeouts (google_api.STT_TIMEOUT), so the browser
// doesn't give up first.
const STT_TIMEOUT_MS = 40000;

export function transcribeSpeech(audio, mimeType, language) {
  return api("/api/stt", {
    method: "POST",
    body: { audio, mime_type: mimeType, language },
    timeoutMs: STT_TIMEOUT_MS,
  });
}
