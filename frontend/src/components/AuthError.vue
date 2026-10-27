<template>
  <div v-if="msg && !dismissed" class="alert alert-danger alert-dismissible" role="alert">
    {{ msg }}
    <button type="button" class="btn-close" aria-label="Close" @click="dismiss"></button>
  </div>
</template>

<script setup>
import { ref, computed, watch } from "vue";
import { useAuth0 } from "@auth0/auth0-vue";

const { error } = useAuth0();
const dismissed = ref(false);

const msg = computed(() => {
  if (!error.value) return "";
  return error.value.message || String(error.value);
});

// Closing removes the focused button, so move focus to the page content.
function dismiss() {
  dismissed.value = true;
  document.getElementById("main")?.focus();
}

watch(msg, () => {
  dismissed.value = false;
});
</script>
