<template>
  <div v-if="msg && !dismissed" class="alert alert-danger alert-dismissible" role="alert">
    {{ msg }}
    <button type="button" class="btn-close" aria-label="Close" @click="dismissed = true"></button>
  </div>
</template>

<script>
export default {
  name: "AuthError",
  data() {
    return { dismissed: false };
  },
  computed: {
    msg() {
      const error = this.$auth.error;
      if (!error) return "";
      return error.message || String(error);
    },
  },
  watch: {
    msg() {
      this.dismissed = false;
    },
  },
};
</script>
