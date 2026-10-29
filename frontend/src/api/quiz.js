import { api } from "./http";

export function startQuiz(practice = false) {
  return api("/api/me/quiz/start", { method: "POST", body: { practice } });
}

// Every action names the quiz start gave out, so a quiz started elsewhere
// since then is refused instead of answered into.
export function answerQuiz(attemptId, index, answer) {
  return api("/api/me/quiz/answer", {
    method: "POST",
    body: { attempt_id: attemptId, index, answer },
  });
}

export function pauseQuiz(attemptId) {
  return api("/api/me/quiz/pause", { method: "POST", body: { attempt_id: attemptId } });
}

export function resumeQuiz(attemptId) {
  return api("/api/me/quiz/resume", { method: "POST", body: { attempt_id: attemptId } });
}

export function submitQuiz(attemptId) {
  return api("/api/me/quiz/submit", { method: "POST", body: { attempt_id: attemptId } });
}
