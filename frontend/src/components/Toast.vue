<template>
  <div class="toast-container" role="status" aria-live="polite">
    <transition-group name="toast">
      <div
        v-for="t in toasts"
        :key="t.id"
        :class="['toast-item', 'toast-' + t.type]"
      >
        {{ t.message }}
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { toastState } from "../stores/toastStore";

const toasts = computed(() => toastState.toasts);
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 1.5rem;
  right: 1.5rem;
  z-index: 2000;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}
.toast-item {
  min-width: 16rem;
  max-width: 22rem;
  padding: 0.85rem 1.2rem;
  border-radius: 10px;
  color: #fff;
  font-family: "Poppins", sans-serif;
  font-weight: 500;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
}
.toast-success {
  background-color: #1e7e34;
}
.toast-error {
  background-color: #dc3545;
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
