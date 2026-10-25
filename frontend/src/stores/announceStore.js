import { ref } from "vue";

// Messages for screen readers only, read out by the visually hidden live
// region in App.vue (toasts already announce themselves).
export const announcement = ref("");

let pending = null;

export function announce(message) {
  // Clear first, then set after a beat, so the same message twice in a row
  // (two wrong answers, say) still counts as a change and is read again.
  announcement.value = "";
  clearTimeout(pending);
  pending = setTimeout(() => {
    announcement.value = message;
  }, 50);
}
