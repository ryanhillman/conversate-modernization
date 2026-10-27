import { ref } from "vue";

// Messages for screen readers only, read out by the visually hidden live
// region in App.vue (toasts already announce themselves).
export const announcement = ref("");

let pending = null;

export function announce(message) {
  // Clear, then set after a beat, so a repeated message is read again.
  announcement.value = "";
  clearTimeout(pending);
  pending = setTimeout(() => {
    announcement.value = message;
  }, 50);
}
