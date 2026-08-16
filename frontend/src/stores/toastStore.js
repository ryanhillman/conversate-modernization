import { reactive } from "vue";

export const toastState = reactive({ toasts: [] });

let counter = 0;

export function showToast(message, type) {
  const id = counter++;
  toastState.toasts.push({ id, message, type });
  setTimeout(() => {
    toastState.toasts = toastState.toasts.filter((t) => t.id !== id);
  }, 3500);
}
