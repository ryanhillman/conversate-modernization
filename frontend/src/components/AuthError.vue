<template>
  <div v-if="msg && !dismissed" class="alert alert-danger alert-dismissible" role="alert">
    {{ msg }}
    <button type="button" class="btn-close" aria-label="Close" @click="dismissed = true"></button>
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

watch(msg, () => {
  dismissed.value = false;
});
</script>
