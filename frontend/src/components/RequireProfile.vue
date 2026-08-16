<template>
  <div v-if="loading" class="loading-state">
    <p>Loading…</p>
  </div>
  <div v-else-if="user">
    <slot :user="user" :set-user="setUser" />
  </div>
  <div v-else class="text-center">
    <SetUsername />
  </div>
</template>

<script>
import { getMe } from "../api/users";
import { showToast } from "../stores/toastStore";
import SetUsername from "./username/SetUsername.vue";

export default {
  name: "RequireProfile",
  components: {
    SetUsername,
  },
  emits: ["loaded"],
  data() {
    return {
      user: null,
      loading: true,
    };
  },
  mounted() {
    getMe()
      .then((data) => {
        this.user = data;
        this.$emit("loaded", data);
      })
      .catch((err) => {
        // A 404 means no profile yet; the slot falls back to the setup form.
        if (err.status !== 404) {
          console.error("Failed to load user:", err);
          showToast("Could not load your profile.", "error");
        }
      })
      .finally(() => {
        this.loading = false;
      });
  },
  methods: {
    setUser(user) {
      this.user = user;
    },
  },
};
</script>
