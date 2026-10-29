<template>
  <form class="set-username" @submit.prevent="saveUsername(username)">
    <h1 id="setup-heading">Set your username!</h1>
    <!-- The heading is the box's label, for screen readers too. -->
    <input
      id="setup-username"
      ref="usernameInput"
      v-model="username"
      class="form-control mb-2 username-input"
      maxlength="100"
      autocomplete="nickname"
      aria-labelledby="setup-heading"
      :aria-describedby="errorMessage ? 'setup-username-error' : undefined"
      :aria-invalid="errorMessage ? 'true' : undefined"
    />
    <p v-if="errorMessage" id="setup-username-error" class="form-error small mb-2">
      {{ errorMessage }}
    </p>
    <!-- Busy buttons use aria-disabled, not disabled: a disabled button loses keyboard focus. -->
    <button
      type="submit"
      class="btn btn-success"
      :class="{ disabled: saving }"
      :disabled="!!validationError || checking || takenUsername"
      :aria-disabled="saving"
    >
      Save
    </button>
  </form>
</template>

<script setup>
import { ref, nextTick } from "vue";
import { useRouter } from "vue-router";
import { createMe } from "../../api/users";
import { useUsernameAvailability } from "../../composables/useUsernameAvailability";
import { setProfile } from "../../stores/profileStore";
import { showToast } from "../../stores/toastStore";

const router = useRouter();

const username = ref("");
const usernameInput = ref(null);
const { checking, takenUsername, validationError, errorMessage, takenOnSave } =
  useUsernameAvailability(username);
const saving = ref(false);

async function saveUsername(name) {
  if (saving.value) return;
  saving.value = true;
  try {
    setProfile(await createMe(name.trim()));
    showToast("Welcome to Conversate!", "success");
    router.push("/");
  } catch (err) {
    saving.value = false;
    if (takenOnSave(err)) {
      // A taken name disables Save, which would drop focus to the page.
      await nextTick();
      usernameInput.value?.focus();
    } else {
      showToast("Could not save username.", "error");
    }
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
.username-input {
  width: 16.25rem;
  max-width: 100%;
}
</style>
