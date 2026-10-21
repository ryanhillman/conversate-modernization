<template>
  <div v-if="loading" class="loading-state">
    <p>Loading…</p>
  </div>
  <div v-else-if="user">
    <slot :user="user" :set-user="setUser" />
  </div>
  <div v-else class="text-center">
    <SetUsername />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { getMe } from "../api/users";
import { showToast } from "../stores/toastStore";
import SetUsername from "./username/SetUsername.vue";

const emit = defineEmits(["loaded"]);

const user = ref(null);
const loading = ref(true);

function setUser(data) {
  user.value = data;
}

onMounted(() => {
  getMe()
    .then((data) => {
      user.value = data;
      emit("loaded", data);
    })
    .catch((err) => {
      // A 404 means no profile yet; the slot falls back to the setup form.
      if (err.status !== 404) {
        console.error("Failed to load user:", err);
        showToast("Could not load your profile.", "error");
      }
    })
    .finally(() => {
      loading.value = false;
    });
});
</script>
