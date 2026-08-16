import { api } from "./http";

export function startQuiz() {
  return api("/api/me/quiz/start", { method: "POST" });
}

export function answerQuiz(index, answer) {
  return api("/api/me/quiz/answer", { method: "POST", body: { index, answer } });
}

export function pauseQuiz() {
  return api("/api/me/quiz/pause", { method: "POST" });
}

export function resumeQuiz() {
  return api("/api/me/quiz/resume", { method: "POST" });
}

export function submitQuiz() {
  return api("/api/me/quiz/submit", { method: "POST" });
}
