<template>
  <div class="d-flex flex-column h-100">
    <Toast />
    <div class="visually-hidden" role="status">{{ announcement }}</div>
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
import { announcement } from "./stores/announceStore";
</script>
