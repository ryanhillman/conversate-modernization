<template>
  <div ref="container" class="toast-container" role="status" aria-live="polite">
    <transition-group name="toast">
      <div
        v-for="t in toasts"
        :key="t.id"
        :class="['toast-item', 'toast-' + t.type]"
        :data-toast-id="t.id"
      >
        <span>{{ t.message }}</span>
        <button
          v-if="t.type === 'error'"
          type="button"
          class="toast-dismiss"
          aria-label="Dismiss"
          @click="dismiss(t.id, $event)"
        >
          ×
        </button>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from "vue";
import { dismissToast, toastState } from "../stores/toastStore";

const toasts = computed(() => toastState.toasts);
const container = ref(null);

// Toasts sit over the page, and browsers only scroll a newly focused control
// into view when it's off-screen, so it could land hidden behind them.
// app.css uses --toast-space to keep focus clear of them and to leave room
// to scroll the page's last controls above them.
function reserveSpace() {
  const root = document.documentElement;
  if (!toasts.value.length) {
    root.style.removeProperty("--toast-space");
    return;
  }
  const top = container.value.getBoundingClientRect().top;
  root.style.setProperty("--toast-space", `${window.innerHeight - top}px`);
  // A new toast can also cover the control that already has focus.
  const focused = document.activeElement?.getBoundingClientRect();
  if (focused && focused.top >= top && focused.top < window.innerHeight) {
    document.activeElement.scrollIntoView({ block: "nearest" });
  }
}

let observer = null;
onMounted(() => {
  observer = new ResizeObserver(reserveSpace);
  observer.observe(container.value);
});
onBeforeUnmount(() => observer.disconnect());

// Removing the toast would drop focus to the page, so move it to the next
// error toast's Dismiss button, or else to the main content.
async function dismiss(id, event) {
  const hadFocus = event.currentTarget === document.activeElement;
  const errors = toasts.value.filter((t) => t.type === "error");
  const index = errors.findIndex((t) => t.id === id);
  const next = errors[index + 1] ?? errors[index - 1];
  dismissToast(id);
  if (!hadFocus) return;
  await nextTick();
  const button = next && container.value?.querySelector(`[data-toast-id="${next.id}"] button`);
  (button ?? document.getElementById("main"))?.focus();
}
</script>

<style scoped>
.toast-container {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  /* Bootstrap allows the full screen width, which the right offset would push
     past the left edge. */
  max-width: calc(100% - 3rem);
  z-index: 2000;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}
/* Bootstrap's .toast-container lets clicks pass through; take them back here. */
.toast-item {
  pointer-events: auto;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
  min-width: 16rem;
  max-width: 22rem;
  padding: 0.85rem 1.2rem;
  border-radius: 10px;
  color: var(--text-on-dark);
  font-family: "Poppins", sans-serif;
  font-weight: 500;
  box-shadow: var(--popup-shadow);
}
.toast-success {
  background-color: var(--success);
}
.toast-error {
  background-color: var(--bs-danger);
}
.toast-dismiss {
  min-width: 1.5rem;
  min-height: 1.5rem;
  background: none;
  border: 0;
  padding: 0 0.25rem;
  color: inherit;
  font-size: 1.25rem;
  line-height: 1;
}
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
</style>
