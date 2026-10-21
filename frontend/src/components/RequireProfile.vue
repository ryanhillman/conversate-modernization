<template>
  <div v-if="loading" class="loading-state">
    <p>Loading…</p>
  </div>
  <div v-else-if="loadFailed" class="card-style text-center">
    <p>Could not load your profile.</p>
    <button class="btn btn-accent" @click="load">Try again</button>
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
const loadFailed = ref(false);

function setUser(data) {
  user.value = data;
}

function load() {
  loading.value = true;
  loadFailed.value = false;
  getMe()
    .then((data) => {
      user.value = data;
      emit("loaded", data);
    })
    .catch((err) => {
      // A 404 means no profile yet; the slot falls back to the setup form.
      // Any other failure (an outage, a network error) is not the same as
      // "no profile" and must not silently fall into that signup flow.
      if (err.status !== 404) {
        console.error("Failed to load user:", err);
        showToast("Could not load your profile.", "error");
        loadFailed.value = true;
      }
    })
    .finally(() => {
      loading.value = false;
    });
}

onMounted(load);
</script>
