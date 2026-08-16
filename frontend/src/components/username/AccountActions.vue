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

<script>
import {
  updateUsername as apiUpdateUsername,
  resetStats as apiResetStats,
} from "../../api/users";
import usernameAvailability from "../../mixins/usernameAvailability";
import { showToast } from "../../stores/toastStore";
export default {
  name: "AccountActions",
  mixins: [usernameAvailability],
  props: {
    currentUsername: { type: String, default: "" },
  },
  emits: ["updated"],
  data() {
    return {
      username: "",
    };
  },
  methods: {
    skipAvailabilityCheck(candidate) {
      return candidate.toLowerCase() === this.currentUsername.trim().toLowerCase();
    },
    updateUsername(username) {
      this.processing = true;
      apiUpdateUsername(username.trim())
        .then((data) => {
          showToast("Username updated", "success");
          this.username = "";
          this.takenUsername = false;
          this.processing = false;
          this.$emit("updated", data);
        })
        .catch(() => {
          this.processing = false;
          showToast("Could not update username.", "error");
        });
    },
    resetProgress() {
      if (confirm("Reset your progress?")) {
        this.processing = true;
        apiResetStats()
          .then(() => {
            this.processing = false;
            showToast("Your progress has been reset", "success");
            this.$router.push("/mastery");
          })
          .catch(() => {
            this.processing = false;
            showToast("Could not reset your progress.", "error");
          });
      }
    },
  },
};
</script>
