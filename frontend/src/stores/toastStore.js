import { reactive } from "vue";

export const toastState = reactive({ toasts: [] });

let counter = 0;

export function showToast(message, type) {
  const id = counter++;
  toastState.toasts.push({ id, message, type });
  // Errors stay until dismissed (WCAG 2.2.1). A success toast only confirms
  // what the page already shows.
  if (type !== "error") setTimeout(() => dismissToast(id), 3500);
}

export function dismissToast(id) {
  toastState.toasts = toastState.toasts.filter((t) => t.id !== id);
}

export function clearErrorToasts() {
  toastState.toasts = toastState.toasts.filter((t) => t.type !== "error");
}
