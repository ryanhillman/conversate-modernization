<template>
  <div v-if="msg && !dismissed" class="alert alert-danger alert-dismissible" role="alert">
    {{ msg }}
    <button type="button" class="btn-close" aria-label="Close" @click="dismissed = true"></button>
  </div>
</template>

<script setup>
import { ref, computed, watch } from "vue";
import { useAuth } from "../composables/useAuth";

const auth = useAuth();
const dismissed = ref(false);

const msg = computed(() => {
  const error = auth.error;
  if (!error) return "";
  return error.message || String(error);
});

watch(msg, () => {
  dismissed.value = false;
});
</script>
