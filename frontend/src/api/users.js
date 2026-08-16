import { api } from "./http";

export function getMe() {
  return api("/api/me");
}

export function createMe(username, email) {
  return api("/api/me", { method: "POST", body: { user_name: username, email } });
}

export function updateUsername(username) {
  return api("/api/me", { method: "PUT", body: { user_name: username } });
}

export function completeLesson(lessonId) {
  return api(`/api/me/lessons/${lessonId}`, { method: "POST" });
}

export function resetStats() {
  return api("/api/me/reset", { method: "POST" });
}

export function checkUsername(username) {
  return api(`/api/usernames/${encodeURIComponent(username)}`);
}
