<template>
  <div class="d-flex flex-column align-items-center">
    <input
      v-model="username"
      placeholder="Edit username"
      aria-label="New username"
      class="form-control mb-2 account-actions-field"
      maxlength="100"
      autocomplete="username"
      aria-describedby="edit-username-error"
    />
    <p v-if="errorMessage" id="edit-username-error" class="form-error small mb-2">
      {{ errorMessage }}
    </p>
    <!-- Busy buttons use aria-disabled, not disabled: a disabled button loses keyboard focus. -->
    <button
      class="btn btn-success mb-2 account-actions-field"
      :class="{ disabled: saving }"
      @click.prevent="updateUsername(username)"
      :disabled="!!validationError || checking || takenUsername"
      :aria-disabled="saving"
    >
      Update username
    </button>
    <button
      class="btn btn-warning mb-2 account-actions-field"
      :class="{ disabled: saving }"
      @click.prevent="resetProgress()"
      :aria-disabled="saving"
    >
      Reset progress
    </button>
    <button
      class="btn btn-danger account-actions-field"
      :class="{ disabled: saving }"
      @click.prevent="deleteAccount()"
      :aria-disabled="saving"
    >
      Delete account
    </button>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import {
  updateUsername as apiUpdateUsername,
  resetStats as apiResetStats,
  deleteMe as apiDeleteMe,
} from "../../api/users";
import { logout } from "../../auth";
import { useUsernameAvailability } from "../../composables/useUsernameAvailability";
import { profile, setProfile } from "../../stores/profileStore";
import { showToast } from "../../stores/toastStore";

const router = useRouter();

const username = ref("");
const { checking, takenUsername, validationError, errorMessage } = useUsernameAvailability(
  username,
  {
    skipAvailabilityCheck: (candidate) =>
      candidate.toLowerCase() === (profile.value?.username ?? "").toLowerCase(),
  },
);
const saving = ref(false);

async function updateUsername(name) {
  if (saving.value) return;
  saving.value = true;
  try {
    const data = await apiUpdateUsername(name.trim());
    showToast("Username updated", "success");
    username.value = "";
    takenUsername.value = false;
    setProfile(data);
  } catch {
    showToast("Could not update username.", "error");
  } finally {
    saving.value = false;
  }
}

async function resetProgress() {
  if (saving.value) return;
  if (confirm("Reset your progress?")) {
    saving.value = true;
    try {
      setProfile(await apiResetStats());
      showToast("Your progress has been reset", "success");
      router.push("/mastery");
    } catch {
      showToast("Could not reset your progress.", "error");
    } finally {
      saving.value = false;
    }
  }
}

async function deleteAccount() {
  if (saving.value) return;
  if (confirm("Delete your account?")) {
    saving.value = true;
    try {
      await apiDeleteMe();
      logout();
    } catch {
      showToast("Could not delete your account.", "error");
      saving.value = false;
    }
  }
}
</script>

<style scoped>
.account-actions-field {
  width: 260px;
}
</style>
