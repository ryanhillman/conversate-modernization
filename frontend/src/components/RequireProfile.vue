<template>
  <div v-if="loading" class="loading-state">
    <p>Loading…</p>
  </div>
  <div v-else-if="loadFailed" class="card-style text-center">
    <p>Could not load your profile.</p>
    <button ref="retryButton" class="btn btn-accent" @click="retry">Try again</button>
  </div>
  <div v-else-if="profile" ref="content" tabindex="-1">
    <slot />
  </div>
  <div v-else ref="content" class="text-center" tabindex="-1">
    <SetUsername />
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from "vue";
import { profile, loadProfile } from "../stores/profileStore";
import SetUsername from "./username/SetUsername.vue";

// Only the first view after sign-in waits; later ones find the profile in the
// store.
const loading = ref(!profile.value);
const loadFailed = ref(false);
const retryButton = ref(null);
const content = ref(null);

async function load() {
  if (profile.value) return;
  loading.value = true;
  loadFailed.value = false;
  try {
    await loadProfile();
  } catch (err) {
    // 404 means no profile yet, so the setup form shows. Other failures
    // aren't "no profile" and mustn't show it.
    if (err.status !== 404) {
      console.error("Failed to load user:", err);
      loadFailed.value = true;
    }
  } finally {
    loading.value = false;
  }
}

// Try again is replaced while loading, so put focus on whatever replaces it.
async function retry() {
  await load();
  await nextTick();
  (loadFailed.value ? retryButton : content).value?.focus();
}

onMounted(load);
</script>
