<template>
  <div class="d-flex flex-column app-shell">
    <a href="#main" class="visually-hidden-focusable">Skip to main content</a>
    <Toast />
    <div class="visually-hidden" role="status">{{ announcement }}</div>
    <NavBar />
    <main id="main" class="container flex-grow-1" tabindex="-1">
      <AuthError />
      <div class="mt-5">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>
    <footer class="bg-light text-center p-3">
      <img src="/logo.png" alt="Conversate logo" width="80" height="80" />
    </footer>
  </div>
</template>

<script setup>
import NavBar from "./components/NavBar.vue";
import AuthError from "./components/AuthError.vue";
import Toast from "./components/Toast.vue";
import { announcement } from "./stores/announceStore";
</script>

<style scoped>
/* At least the window's height, so the footer sits at the bottom of short
   pages; longer pages grow it, which keeps the room reserved below the footer
   for toasts (app.css) scrollable. */
.app-shell {
  min-height: 100%;
}
</style>
