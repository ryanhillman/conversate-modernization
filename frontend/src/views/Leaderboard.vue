<template>
  <RequireProfile>
    <div class="text-center">
      <div class="card-style">
        <h1 class="h2">Leaderboard</h1>
      </div>

      <div v-if="loading" class="loading-state">
        <p>Loading…</p>
      </div>
      <div v-else-if="loadFailed" class="card-style">
        <p>Could not load the leaderboard.</p>
        <button ref="retryButton" class="btn btn-accent" @click="retry">Try again</button>
      </div>
      <div v-else ref="results" tabindex="-1">
        <p v-if="!rows.length" class="text-muted">No quiz results yet — be the first!</p>
        <div v-else class="leaderboard-wrap">
          <table class="leaderboard-table">
            <caption class="visually-hidden">
              Top quiz scores
            </caption>
            <thead>
              <tr>
                <th>Rank</th>
                <th>Player</th>
                <th>Correct</th>
                <th>Time</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(row, index) in rows"
                :key="row.username"
                :class="{ 'leaderboard-you': isYou(row) }"
              >
                <td>{{ index + 1 }}</td>
                <td>
                  {{ row.username }}<span v-if="isYou(row)" class="visually-hidden"> (you)</span>
                </td>
                <td>{{ row.score }}</td>
                <td>{{ formatTime(row.time_seconds) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </RequireProfile>
</template>

<script setup>
import { ref, nextTick, onMounted } from "vue";
import RequireProfile from "../components/RequireProfile.vue";
import { getLeaderboard } from "../api/leaderboard";
import { announce } from "../stores/announceStore";
import { profile as user } from "../stores/profileStore";
import { formatTime } from "../utils/formatTime";

const rows = ref([]);
const loading = ref(true);
const loadFailed = ref(false);
const retryButton = ref(null);
const results = ref(null);

function isYou(row) {
  return user.value && row.username === user.value.username;
}

async function load() {
  loading.value = true;
  loadFailed.value = false;
  try {
    rows.value = await getLeaderboard();
    // The result replaces "Loading…" while focus stays put, so say which it was.
    announce("Leaderboard loaded.");
  } catch (err) {
    console.error("Failed to load leaderboard:", err);
    loadFailed.value = true;
    announce("Could not load the leaderboard.");
  } finally {
    loading.value = false;
  }
}

// Try again is replaced while loading, so put focus on whatever replaces it.
async function retry() {
  await load();
  await nextTick();
  (loadFailed.value ? retryButton : results).value?.focus();
}

onMounted(load);
</script>

<style scoped>
.leaderboard-wrap {
  max-width: 40rem;
  margin: 0 auto;
}
.leaderboard-table {
  width: 100%;
  background-color: var(--card-bg);
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: var(--card-shadow);
}
.leaderboard-table th,
.leaderboard-table td {
  padding: 0.75rem 1rem;
  text-align: center;
  border-bottom: 1px solid var(--border-subtle);
  overflow-wrap: anywhere;
}
.leaderboard-table th {
  background-color: var(--brand-navy);
  color: var(--text-on-dark);
}
.leaderboard-you {
  background-color: color-mix(in srgb, var(--brand-accent) 18%, transparent);
  font-weight: 600;
}
</style>
