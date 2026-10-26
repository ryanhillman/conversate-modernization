import { api } from "./http";

// Above the backend's timeouts for the Google call (google_api.STT_TIMEOUT:
// 8s connect, 8s write, 20s read), so the browser doesn't give up while the
// backend is still waiting on Google.
const STT_TIMEOUT_MS = 40000;

export function transcribeSpeech(audio, mimeType, language) {
  return api("/api/stt", {
    method: "POST",
    body: { audio, mime_type: mimeType, language },
    timeoutMs: STT_TIMEOUT_MS,
  });
}
