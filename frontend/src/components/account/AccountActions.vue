<template>
  <div class="d-flex flex-column align-items-center">
    <label for="new-username" class="account-actions-field text-start mb-2">New username</label>
    <input
      id="new-username"
      ref="usernameInput"
      v-model="username"
      class="form-control mb-2 account-actions-field"
      maxlength="100"
      autocomplete="username"
      :aria-describedby="errorMessage ? 'edit-username-error' : undefined"
      :aria-invalid="errorMessage ? 'true' : undefined"
    />
    <p v-if="errorMessage" id="edit-username-error" class="form-error small mb-2">
      {{ errorMessage }}
    </p>
    <!-- Busy buttons use aria-disabled, not disabled: a disabled button loses keyboard focus. -->
    <button
      class="btn btn-success mb-2 account-actions-field"
      :class="{ disabled: saving }"
      :disabled="!!validationError || checking || takenUsername"
      :aria-disabled="saving"
      @click="updateUsername(username)"
    >
      Update username
    </button>
    <button
      class="btn btn-warning mb-2 account-actions-field"
      :class="{ disabled: saving }"
      :aria-disabled="saving"
      @click="resetProgress()"
    >
      Reset progress
    </button>
    <button
      class="btn btn-danger account-actions-field"
      :class="{ disabled: saving }"
      :aria-disabled="saving"
      @click="deleteAccount()"
    >
      Delete account
    </button>
  </div>
</template>

<script setup>
import { ref, nextTick } from "vue";
import { useRouter } from "vue-router";
import {
  updateUsername as apiUpdateUsername,
  resetProgress as apiResetProgress,
  deleteMe as apiDeleteMe,
} from "../../api/users";
import { logout } from "../../auth";
import { useUsernameAvailability } from "../../composables/useUsernameAvailability";
import { profile, setProfile } from "../../stores/profileStore";
import { showToast } from "../../stores/toastStore";

const router = useRouter();

const username = ref("");
const usernameInput = ref(null);
const { checking, takenUsername, validationError, errorMessage, takenOnSave } =
  useUsernameAvailability(username, {
    skipAvailabilityCheck: (candidate) =>
      candidate.toLowerCase() === (profile.value?.username ?? "").toLowerCase(),
  });
const saving = ref(false);

async function updateUsername(name) {
  if (saving.value) return;
  saving.value = true;
  try {
    const data = await apiUpdateUsername(name.trim());
    showToast("Username updated", "success");
    username.value = "";
    setProfile(data);
    // Clearing the box disables Update, which would drop focus to the page.
    await nextTick();
    usernameInput.value?.focus();
  } catch (err) {
    if (takenOnSave(err)) {
      // A taken name disables Update, which would drop focus to the page.
      await nextTick();
      usernameInput.value?.focus();
    } else {
      showToast("Could not update username.", "error");
    }
  } finally {
    saving.value = false;
  }
}

async function resetProgress() {
  if (saving.value) return;
  if (confirm("Reset your progress? This can't be undone.")) {
    saving.value = true;
    try {
      setProfile(await apiResetProgress());
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
  if (confirm("Delete your account? This can't be undone.")) {
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
  width: 16.25rem;
  max-width: 100%;
}
</style>
