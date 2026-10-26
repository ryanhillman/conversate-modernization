<template>
  <RequireProfile>
    <div class="text-center">
      <div class="card-style">
        <h2>Leaderboard</h2>
      </div>

      <div v-if="loading" class="loading-state">
        <p>Loading…</p>
      </div>
      <p v-else-if="!rows.length" class="text-muted">No quiz results yet — be the first!</p>
      <div v-else class="leaderboard-wrap">
        <table class="leaderboard-table">
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
  </RequireProfile>
</template>

<script setup>
import { ref, onMounted } from "vue";
import RequireProfile from "../components/RequireProfile.vue";
import { getLeaderboard } from "../api/leaderboard";
import { profile as user } from "../stores/profileStore";
import { showToast } from "../stores/toastStore";
import { formatTime } from "../utils/formatTime";

const rows = ref([]);
const loading = ref(true);

function isYou(row) {
  return user.value && row.username === user.value.username;
}

onMounted(async () => {
  try {
    rows.value = await getLeaderboard();
  } catch (err) {
    console.error("Failed to load leaderboard:", err);
    showToast("Could not load the leaderboard.", "error");
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.leaderboard-wrap {
  max-width: 40rem;
  margin: 0 auto;
}
.leaderboard-table {
  width: 100%;
  border-collapse: collapse;
  background-color: var(--card-bg);
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: var(--card-shadow);
}
.leaderboard-table th,
.leaderboard-table td {
  padding: 0.75rem 1rem;
  text-align: center;
  border-bottom: 1px solid #e5e9f0;
  overflow-wrap: anywhere;
}
.leaderboard-table th {
  background-color: var(--brand-navy);
  color: white;
}
.leaderboard-you {
  background-color: color-mix(in srgb, var(--brand-accent) 18%, transparent);
  font-weight: 600;
}
</style>
