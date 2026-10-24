<template>
  <div class="mb-3">
    <nav class="navbar navbar-expand-xl navbar-light bg-light">
      <div class="container" :class="{ 'nav-guest': !$auth.isAuthenticated }">
        <div class="nav-side nav-left">
          <img src="/logo.png" alt="Conversate logo" width="100" height="100" />
        </div>
        <button
          class="navbar-toggler"
          type="button"
          aria-controls="navbarNav"
          :aria-expanded="navOpen ? 'true' : 'false'"
          aria-label="Toggle navigation"
          @click="navOpen = !navOpen"
        >
          <span class="navbar-toggler-icon"></span>
        </button>

        <div id="navbarNav" class="collapse navbar-collapse" :class="{ show: navOpen }">
          <ul class="navbar-nav">
            <li v-if="$auth.isAuthenticated" class="nav-item">
              <router-link to="/" class="nav-link"><span class="nav-label">Home</span></router-link>
            </li>
            <li v-if="$auth.isAuthenticated" class="nav-item">
              <router-link to="/profile" class="nav-link"
                ><span class="nav-label">Profile</span></router-link
              >
            </li>
            <li v-if="$auth.isAuthenticated" class="nav-item">
              <router-link to="/mastery" class="nav-link"
                ><span class="nav-label">Mastery</span></router-link
              >
            </li>
            <li v-if="$auth.isAuthenticated" class="nav-item">
              <router-link to="/lesson" class="nav-link"
                ><span class="nav-label">Lessons</span></router-link
              >
            </li>
            <li v-if="$auth.isAuthenticated" class="nav-item">
              <router-link to="/translate" class="nav-link"
                ><span class="nav-label">Translate</span></router-link
              >
            </li>
            <li v-if="$auth.isAuthenticated" class="nav-item">
              <router-link to="/quiz" class="nav-link"
                ><span class="nav-label">Quiz</span></router-link
              >
            </li>
            <li v-if="$auth.isAuthenticated" class="nav-item">
              <router-link to="/leaderboard" class="nav-link"
                ><span class="nav-label">Leaderboard</span></router-link
              >
            </li>
          </ul>

          <ul class="navbar-nav d-xl-none" v-if="!$auth.isAuthenticated && !$auth.loading">
            <li class="nav-item">
              <button class="btn btn-primary w-100" @click="login">Log in</button>
            </li>
          </ul>

          <ul
            id="mobileAuthNavBar"
            class="navbar-nav d-xl-none d-flex"
            v-if="$auth.isAuthenticated"
          >
            <li class="nav-item">
              <span class="user-info">
                <img
                  :src="$auth.user.picture"
                  alt="User's profile picture"
                  class="nav-user-profile d-inline-block rounded-circle me-3"
                  width="50"
                />
                <h6 class="d-inline-block">{{ $auth.user.name }}</h6>
              </span>
            </li>

            <li>
              <Icon name="power-off" class="me-3" />
              <a href="#" @click.prevent="logout">Log out</a>
            </li>
          </ul>
        </div>

        <ul class="navbar-nav nav-side nav-right d-none d-xl-flex">
          <li v-if="!$auth.isAuthenticated && !$auth.loading" class="nav-item">
            <button class="btn btn-primary" @click.prevent="login">Log in</button>
          </li>

          <li
            v-if="$auth.isAuthenticated"
            ref="dropdown"
            class="nav-item dropdown"
            :class="{ show: dropdownOpen }"
          >
            <a
              class="nav-link dropdown-toggle"
              href="#"
              id="profileDropDown"
              aria-haspopup="true"
              :aria-expanded="dropdownOpen ? 'true' : 'false'"
              @click.prevent="dropdownOpen = !dropdownOpen"
            >
              <img
                :src="$auth.user.picture"
                alt="User's profile picture"
                class="nav-user-profile rounded-circle"
                width="50"
              />
            </a>
            <div
              class="dropdown-menu dropdown-menu-end"
              :class="{ show: dropdownOpen }"
              aria-labelledby="profileDropDown"
            >
              <div class="dropdown-header">{{ $auth.user.name }}</div>
              <a href="#" class="dropdown-item" @click.prevent="logout">
                <Icon name="power-off" class="me-3" />Log out
              </a>
            </div>
          </li>
        </ul>
      </div>
    </nav>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from "vue";
import { useRoute } from "vue-router";
import Icon from "./Icon.vue";
import { useAuth } from "../composables/useAuth";
import { clearProfile } from "../stores/profileStore";

const auth = useAuth();
const route = useRoute();

const navOpen = ref(false);
const dropdownOpen = ref(false);
const dropdown = ref(null);

watch(
  () => route.fullPath,
  () => {
    navOpen.value = false;
    dropdownOpen.value = false;
  },
);

function onDocumentClick(event) {
  if (dropdownOpen.value && dropdown.value && !dropdown.value.contains(event.target)) {
    dropdownOpen.value = false;
  }
}

onMounted(() => {
  document.addEventListener("click", onDocumentClick);
});
onBeforeUnmount(() => {
  document.removeEventListener("click", onDocumentClick);
});

function login() {
  auth.loginWithRedirect();
}
function logout() {
  clearProfile();
  auth.logout();
}
</script>

<style scoped>
#mobileAuthNavBar {
  min-height: 125px;
  justify-content: space-between;
}
.nav-link {
  margin: 0;
  padding: 0.85rem 0.9rem;
  min-width: 7.5rem;
  text-align: center;
  color: var(--text-color);
  transition: color 0.15s ease;
}
.nav-link:hover,
.nav-link:focus-visible {
  color: var(--brand-navy);
}
.nav-label {
  display: inline-block;
  padding-bottom: 0.35rem;
  border-bottom: 3px solid transparent;
  transition: border-color 0.15s ease;
}
.router-link-active {
  color: var(--brand-navy);
}
.router-link-active .nav-label {
  border-bottom-color: var(--brand-navy);
}
@media (min-width: 1200px) {
  .container {
    position: relative;
  }
  .nav-side {
    flex: 1 1 0;
    display: flex;
    align-items: center;
  }
  .nav-right {
    justify-content: flex-end;
  }
  #navbarNav > .navbar-nav {
    gap: 0.15rem;
  }
  .container:not(.nav-guest) #navbarNav {
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
  }
}
</style>
