<template>
  <div class="d-flex flex-column h-100">
    <Toast />
    <NavBar />
    <div class="container flex-grow-1">
      <AuthError />
      <div class="mt-5">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </div>
    <footer class="bg-light text-center p-3">
      <img src="/logo.png" alt="Conversate logo" width="80" height="80" />
    </footer>
  </div>
</template>

<script setup>
import NavBar from "./components/NavBar.vue";
import AuthError from "./components/AuthError.vue";
import Toast from "./components/Toast.vue";
</script>

<style>
:root {
  --brand-navy: #16335c;
  --brand-navy-dark: #0f2547;
  --brand-accent: #e0a82e;
  --brand-accent-dark: #c8901a;
  --success: #1e7e34;
  --danger-text: #b02a37;
  --page-bg: #d8dee8;
  --text-color: #1f2937;
  --text-muted: var(--bs-secondary-color);
  --card-shadow: 0 4px 8px rgba(0, 0, 0, 0.1), 0 10px 24px rgba(0, 0, 0, 0.18);
  --card-border: 1px solid #bcc5d2;
  --card-bg: #ffffff;
  --radius: 12px;
}

body {
  font-family:
    "Inter",
    -apple-system,
    BlinkMacSystemFont,
    "Segoe UI",
    sans-serif;
  background-color: var(--page-bg);
  color: var(--text-color);
}

.card {
  background-color: var(--card-bg);
  color: var(--text-color);
}

h1,
h2,
h3,
h4,
h5,
h6 {
  font-family: "Poppins", sans-serif;
  font-weight: 600;
}

.btn {
  font-family: "Poppins", sans-serif;
  font-weight: 500;
  border-radius: 8px;
  user-select: none;
}

.btn-primary {
  background-color: var(--brand-navy);
  border-color: var(--brand-navy);
}

.btn-primary:hover {
  background-color: var(--brand-navy-dark);
  border-color: var(--brand-navy-dark);
}

.btn-accent {
  background-color: var(--brand-accent);
  border-color: var(--brand-accent);
  color: var(--text-color);
  font-family: "Poppins", sans-serif;
  font-weight: 500;
  border-radius: 8px;
}

.btn-accent:hover {
  background-color: var(--brand-accent-dark);
  border-color: var(--brand-accent-dark);
  color: var(--text-color);
}

.card-style {
  border-radius: var(--radius);
  box-shadow: var(--card-shadow);
  padding: 1.5rem;
  margin: 2rem auto;
  max-width: 40rem;
  color: white;
  background-color: var(--brand-navy);
  font-weight: 400;
  text-align: center;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Bootstrap's default input borders are too faint to see (WCAG asks for
   3:1); use its own secondary gray. */
.form-control,
.form-select {
  border-color: var(--bs-secondary);
}

/* Bootstrap's darker red: its main red fails contrast on the gray page. */
.form-error {
  color: var(--danger-text);
}

.loading-state {
  text-align: center;
  margin: 3rem auto;
  color: var(--text-muted);
  font-size: 1.2rem;
}
</style>
