<template>
  <RequireProfile @loaded="user = $event">
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
              :key="row.user_name"
              :class="{ 'leaderboard-you': user && row.user_name === user.user_name }"
            >
              <td>{{ index + 1 }}</td>
              <td>{{ row.user_name }}</td>
              <td>{{ row.score }}</td>
              <td>{{ formattedTime(row.time_seconds) }}</td>
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
import { showToast } from "../stores/toastStore";
import { formatTime as formattedTime } from "../utils/formatTime";

const user = ref(null);
const rows = ref([]);
const loading = ref(true);

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
  background-color: rgba(224, 168, 46, 0.18);
  font-weight: 600;
}
</style>
