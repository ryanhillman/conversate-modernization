<template>
  <div class="set-username">
    <h1>Set your username!</h1>
    <input
      v-model="username"
      placeholder="Username"
      class="username-input"
      maxlength="100"
      aria-label="Username"
    />
    <p v-if="username && validationError" class="text-danger small mb-2">{{ validationError }}</p>
    <p v-else-if="takenUsername" class="text-danger small mb-2">That username is taken</p>
    <br />
    <button
      class="btn btn-success"
      @click.prevent="saveUsername(username)"
      :disabled="!!validationError || processing || takenUsername"
    >
      Save username
    </button>
  </div>
</template>

<script>
import { createMe } from "../../api/users";
import usernameAvailability from "../../mixins/usernameAvailability";
import { showToast } from "../../stores/toastStore";
export default {
  name: "SetUsername",
  mixins: [usernameAvailability],
  data() {
    return {
      username: "",
    };
  },
  methods: {
    saveUsername(username) {
      this.processing = true;
      createMe(username.trim(), this.$auth.user.email)
        .then(() => {
          showToast("Welcome to Conversate!", "success");
          this.$router.push("/");
        })
        .catch(() => {
          this.processing = false;
          showToast("Could not save username.", "error");
        });
    },
  },
};
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
  width: 260px;
  padding: 0.5rem 0.75rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  margin-bottom: 1rem;
}
</style>

