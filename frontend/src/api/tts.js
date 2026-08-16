import { api } from "./http";

export function synthesizeSpeech(text, language) {
  return api("/api/tts", { method: "POST", body: { text, language } });
}
