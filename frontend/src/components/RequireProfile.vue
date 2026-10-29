<template>
  <!-- The page's h1 is in the slot, which these states replace, so they need their own. -->
  <div v-if="loading" class="loading-state">
    <h1 class="visually-hidden">{{ route.meta.title }}</h1>
    <p>Loading…</p>
  </div>
  <div v-else-if="loadFailed" class="card-style">
    <h1 class="visually-hidden">{{ route.meta.title }}</h1>
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
import { ref, computed, watch, nextTick, onMounted } from "vue";
import { useRoute } from "vue-router";
import { announce } from "../stores/announceStore";
import { profile, loadProfile } from "../stores/profileStore";
import { pageTitle } from "../utils/pageTitle";
import SetUsername from "./account/SetUsername.vue";

const route = useRoute();

// Only the first view after sign-in waits; later ones find the profile in the
// store.
const loading = ref(!profile.value);
const loadFailed = ref(false);
const retryButton = ref(null);
const content = ref(null);

// The setup form replaces the page that was asked for, so title it instead.
const settingUp = computed(() => !loading.value && !loadFailed.value && !profile.value);
watch(settingUp, (value) => {
  if (value) document.title = pageTitle("Set your username");
});

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
      announce("Could not load your profile.");
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
