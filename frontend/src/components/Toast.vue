<template>
  <div class="toast-container" role="status" aria-live="polite">
    <transition-group name="toast">
      <div v-for="t in toasts" :key="t.id" :class="['toast-item', 'toast-' + t.type]">
        <span>{{ t.message }}</span>
        <button
          v-if="t.type === 'error'"
          type="button"
          class="toast-dismiss"
          aria-label="Dismiss"
          @click="dismissToast(t.id)"
        >
          ×
        </button>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { dismissToast, toastState } from "../stores/toastStore";

const toasts = computed(() => toastState.toasts);
</script>

<style scoped>
.toast-container {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
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
