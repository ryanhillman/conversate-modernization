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
              ref="dropdownToggle"
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

const auth = useAuth();
const route = useRoute();

const navOpen = ref(false);
const dropdownOpen = ref(false);
const dropdown = ref(null);
const dropdownToggle = ref(null);

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

// Escape closes the menu and returns focus to the profile picture that opened
// it, the standard behavior for dropdown menus.
function onDocumentKeydown(event) {
  if (event.key === "Escape" && dropdownOpen.value) {
    dropdownOpen.value = false;
    dropdownToggle.value?.focus();
  }
}

onMounted(() => {
  document.addEventListener("click", onDocumentClick);
  document.addEventListener("keydown", onDocumentKeydown);
});
onBeforeUnmount(() => {
  document.removeEventListener("click", onDocumentClick);
  document.removeEventListener("keydown", onDocumentKeydown);
});

function login() {
  auth.loginWithRedirect();
}
// Logout leaves for Auth0 and comes back with a full page load, which resets
// the profile store. Clearing it first would briefly show the username setup
// form on the current page.
function logout() {
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
  position: relative;
  display: inline-block;
  padding-bottom: 0.35rem;
  border-bottom: 3px solid transparent;
}
/* Underline: grows out from the center on hover, and is always shown for the
   current page. It sits over the label's transparent border. */
.nav-label::after {
  content: "";
  position: absolute;
  left: 0;
  right: 0;
  bottom: -3px;
  height: 3px;
  background-color: var(--brand-navy);
  transform: scaleX(0);
  transition: transform 0.2s ease;
}
.nav-link:hover .nav-label::after,
.nav-link:focus-visible .nav-label::after {
  transform: scaleX(1);
}
/* The current page shows the same underline at full width, so both always
   match exactly. */
.router-link-active .nav-label::after {
  transform: scaleX(1);
}
@media (prefers-reduced-motion: reduce) {
  .nav-label::after {
    transition: none;
  }
}
/* Gold hover glow on Log in, like the home cards. Keyboard focus keeps
   Bootstrap's own focus ring. */
.navbar-nav .btn-primary {
  transition: box-shadow 0.15s ease;
}
.navbar-nav .btn-primary:hover {
  box-shadow: 0 0 12px rgba(224, 168, 46, 0.6);
}
/* Gold ring on the profile picture while hovered or while its menu is open. */
#profileDropDown .nav-user-profile {
  transition: box-shadow 0.15s ease;
}
#profileDropDown:hover .nav-user-profile,
#profileDropDown[aria-expanded="true"] .nav-user-profile {
  box-shadow:
    0 0 0 3px rgba(224, 168, 46, 0.7),
    0 0 10px rgba(224, 168, 46, 0.5);
}
.router-link-active {
  color: var(--brand-navy);
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
