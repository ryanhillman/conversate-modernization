<template>
  <div v-if="loading" class="loading-state">
    <p>Loading…</p>
  </div>
  <div v-else-if="loadFailed" class="card-style text-center">
    <p>Could not load your profile.</p>
    <button class="btn btn-accent" @click="load">Try again</button>
  </div>
  <div v-else-if="profile">
    <slot :user="profile" :set-user="setProfile" />
  </div>
  <div v-else class="text-center">
    <SetUsername />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { profile, loadProfile, setProfile } from "../stores/profileStore";
import { showToast } from "../stores/toastStore";
import SetUsername from "./username/SetUsername.vue";

// Only the first view after sign-in (or a reload) waits on the request;
// later views find the profile already in the store and render immediately.
const loading = ref(!profile.value);
const loadFailed = ref(false);

async function load() {
  if (profile.value) return;
  loading.value = true;
  loadFailed.value = false;
  try {
    await loadProfile();
  } catch (err) {
    // A 404 means no profile yet; the slot falls back to the setup form.
    // Any other failure (an outage, a network error) is not the same as
    // "no profile" and must not silently fall into that signup flow.
    if (err.status !== 404) {
      console.error("Failed to load user:", err);
      showToast("Could not load your profile.", "error");
      loadFailed.value = true;
    }
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>
