import { api } from "./http";

export function transcribeSpeech(audio, mimeType, language) {
  return api("/api/stt", { method: "POST", body: { audio, mime_type: mimeType, language } });
}
