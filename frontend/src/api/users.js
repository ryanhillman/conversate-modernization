import { api } from "./http";

export function getMe() {
  return api("/api/me");
}

export function createMe(username) {
  return api("/api/me", { method: "POST", body: { username } });
}

export function updateUsername(username) {
  return api("/api/me", { method: "PUT", body: { username } });
}

export function completeLesson(lessonId) {
  return api(`/api/me/lessons/${lessonId}`, { method: "POST" });
}

export function resetProgress() {
  return api("/api/me/reset", { method: "POST" });
}

export function deleteMe() {
  return api("/api/me", { method: "DELETE" });
}

export function checkUsername(username) {
  return api(`/api/usernames/${encodeURIComponent(username)}`);
}
