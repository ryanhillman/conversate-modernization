<template>
  <div class="d-flex flex-column align-items-center">
    <input
      v-model="username"
      placeholder="Edit username"
      class="form-control mb-2"
      maxlength="100"
      style="width: 260px;"
    />
    <p v-if="username && validationError" class="text-danger small mb-2">{{ validationError }}</p>
    <p v-else-if="takenUsername" class="text-danger small mb-2">That username is taken</p>
    <button
      class="btn btn-success mb-2"
      style="width: 260px;"
      @click.prevent="updateUsername(username)"
      :disabled="!!validationError || processing || takenUsername"
    >
      Update username
    </button>
    <button
      class="btn btn-warning"
      style="width: 260px;"
      @click.prevent="resetProgress()"
      :disabled="processing"
    >
      Reset progress
    </button>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import {
  updateUsername as apiUpdateUsername,
  resetStats as apiResetStats,
} from "../../api/users";
import { useUsernameAvailability } from "../../composables/useUsernameAvailability";
import { showToast } from "../../stores/toastStore";

const props = defineProps({
  currentUsername: { type: String, default: "" },
});
const emit = defineEmits(["updated"]);

const router = useRouter();

const username = ref("");
const { processing, takenUsername, validationError } = useUsernameAvailability(username, {
  skipAvailabilityCheck: (candidate) =>
    candidate.toLowerCase() === props.currentUsername.trim().toLowerCase(),
});

function updateUsername(name) {
  processing.value = true;
  apiUpdateUsername(name.trim())
    .then((data) => {
      showToast("Username updated", "success");
      username.value = "";
      takenUsername.value = false;
      processing.value = false;
      emit("updated", data);
    })
    .catch(() => {
      processing.value = false;
      showToast("Could not update username.", "error");
    });
}

function resetProgress() {
  if (confirm("Reset your progress?")) {
    processing.value = true;
    apiResetStats()
      .then(() => {
        processing.value = false;
        showToast("Your progress has been reset", "success");
        router.push("/mastery");
      })
      .catch(() => {
        processing.value = false;
        showToast("Could not reset your progress.", "error");
      });
  }
}
</script>
