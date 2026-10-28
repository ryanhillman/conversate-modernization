<template>
  <div class="set-username">
    <h1>Set your username!</h1>
    <label for="setup-username" class="username-label">Username</label>
    <input
      id="setup-username"
      v-model="username"
      class="form-control mb-2 username-input"
      maxlength="100"
      autocomplete="username"
      aria-describedby="setup-username-error"
    />
    <p v-if="errorMessage" id="setup-username-error" class="form-error small mb-2">
      {{ errorMessage }}
    </p>
    <!-- Busy buttons use aria-disabled, not disabled: a disabled button loses keyboard focus. -->
    <button
      class="btn btn-success"
      :class="{ disabled: saving }"
      :disabled="!!validationError || checking || takenUsername"
      :aria-disabled="saving"
      @click.prevent="saveUsername(username)"
    >
      Save username
    </button>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { createMe } from "../../api/users";
import { useUsernameAvailability } from "../../composables/useUsernameAvailability";
import { setProfile } from "../../stores/profileStore";
import { showToast } from "../../stores/toastStore";

const router = useRouter();

const username = ref("");
const { checking, takenUsername, validationError, errorMessage } =
  useUsernameAvailability(username);
const saving = ref(false);

async function saveUsername(name) {
  if (saving.value) return;
  saving.value = true;
  try {
    setProfile(await createMe(name.trim()));
    showToast("Welcome to Conversate!", "success");
    router.push("/");
  } catch {
    saving.value = false;
    showToast("Could not save username.", "error");
  }
}
</script>

<style scoped>
.set-username {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  max-width: 40rem;
  margin: 2rem auto;
}
/* In rem, so they grow with a larger default text size. */
.username-label {
  width: 16.25rem;
  max-width: 100%;
  text-align: start;
  margin-bottom: 0.5rem;
}
.username-input {
  width: 16.25rem;
  max-width: 100%;
}
</style>
