<template>
  <div class="d-flex flex-column align-items-center">
    <input
      v-model="username"
      placeholder="Edit username"
      aria-label="New username"
      class="form-control mb-2 account-actions-field"
      maxlength="100"
      aria-describedby="edit-username-error"
    />
    <p v-if="username && validationError" id="edit-username-error" class="form-error small mb-2">
      {{ validationError }}
    </p>
    <p v-else-if="takenUsername" id="edit-username-error" class="form-error small mb-2">
      That username is taken
    </p>
    <button
      class="btn btn-success mb-2 account-actions-field"
      @click.prevent="updateUsername(username)"
      :disabled="!!validationError || checking || saving || takenUsername"
    >
      Update username
    </button>
    <button
      class="btn btn-warning mb-2 account-actions-field"
      @click.prevent="resetProgress()"
      :disabled="saving"
    >
      Reset progress
    </button>
    <button
      class="btn btn-danger account-actions-field"
      @click.prevent="deleteAccount()"
      :disabled="saving"
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
import { useAuth } from "../../composables/useAuth";
import { useUsernameAvailability } from "../../composables/useUsernameAvailability";
import { setProfile } from "../../stores/profileStore";
import { showToast } from "../../stores/toastStore";

const props = defineProps({
  currentUsername: { type: String, default: "" },
});
const emit = defineEmits(["updated"]);

const router = useRouter();
const auth = useAuth();

const username = ref("");
const { checking, takenUsername, validationError } = useUsernameAvailability(username, {
  skipAvailabilityCheck: (candidate) =>
    candidate.toLowerCase() === props.currentUsername.trim().toLowerCase(),
});
const saving = ref(false);

async function updateUsername(name) {
  saving.value = true;
  try {
    const data = await apiUpdateUsername(name.trim());
    showToast("Username updated", "success");
    username.value = "";
    takenUsername.value = false;
    emit("updated", data);
  } catch {
    showToast("Could not update username.", "error");
  } finally {
    saving.value = false;
  }
}

async function resetProgress() {
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
  if (confirm("Delete your account?")) {
    saving.value = true;
    try {
      await apiDeleteMe();
      auth.logout();
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
