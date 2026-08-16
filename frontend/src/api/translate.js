import { api } from "./http";

export function translateText(text, source, target) {
  return api("/api/translate", { method: "POST", body: { text, source, target } });
}
