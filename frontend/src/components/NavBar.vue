<template>
  <div class="mb-3">
    <nav class="navbar navbar-expand-xl navbar-light bg-light">
      <div class="container" :class="{ 'nav-guest': !isAuthenticated }">
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
            <template v-if="isAuthenticated">
              <li v-for="page in pages" :key="page.path" class="nav-item">
                <router-link :to="page.path" class="nav-link"
                  ><span class="nav-label">{{ page.label }}</span></router-link
                >
              </li>
            </template>
          </ul>

          <ul v-if="!isAuthenticated && !isLoading" class="navbar-nav d-xl-none">
            <li class="nav-item">
              <button class="btn btn-primary w-100" @click="login">Log in</button>
            </li>
          </ul>

          <ul v-if="isAuthenticated" id="mobileAuthNavBar" class="navbar-nav d-xl-none d-flex">
            <li class="nav-item">
              <span class="user-info">
                <img
                  :src="user.picture"
                  alt=""
                  referrerpolicy="no-referrer"
                  class="nav-user-profile d-inline-block rounded-circle me-3"
                  width="50"
                />
                <span class="d-inline-block nav-user-name">{{ user.name }}</span>
              </span>
            </li>

            <li>
              <Icon name="power-off" class="me-3" />
              <button type="button" class="nav-logout" @click="logout">Log out</button>
            </li>
          </ul>
        </div>

        <ul class="navbar-nav nav-side nav-right d-none d-xl-flex">
          <li v-if="!isAuthenticated && !isLoading" class="nav-item">
            <button class="btn btn-primary" @click="login">Log in</button>
          </li>

          <li
            v-if="isAuthenticated"
            ref="dropdown"
            class="nav-item dropdown"
            :class="{ show: dropdownOpen }"
            @focusout="onDropdownFocusOut"
          >
            <!-- A disclosure: a button that shows and hides the menu below it,
                 not an ARIA menu with arrow-key navigation. -->
            <button
              id="profileDropDown"
              ref="dropdownToggle"
              type="button"
              class="nav-link dropdown-toggle"
              aria-controls="profileMenu"
              :aria-expanded="dropdownOpen ? 'true' : 'false'"
              @click="dropdownOpen = !dropdownOpen"
            >
              <img
                :src="user.picture"
                alt="Account menu"
                referrerpolicy="no-referrer"
                class="nav-user-profile rounded-circle"
                width="50"
              />
            </button>
            <div
              id="profileMenu"
              class="dropdown-menu dropdown-menu-end"
              :class="{ show: dropdownOpen }"
            >
              <div class="dropdown-header">{{ user.name }}</div>
              <button type="button" class="dropdown-item" @click="logout">
                <Icon name="power-off" class="me-3" />Log out
              </button>
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
import { useAuth0 } from "@auth0/auth0-vue";
import Icon from "./Icon.vue";
import { logout } from "../auth";
import { pages } from "../router/pages";

const auth0 = useAuth0();
const { isAuthenticated, isLoading, user } = auth0;
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

// Tabbing out of the menu closes it. When focus goes nowhere (a click on the
// page, or Safari not focusing a clicked button), the click handler decides,
// so a click on Log out isn't lost.
function onDropdownFocusOut(event) {
  if (event.relatedTarget && !dropdown.value.contains(event.relatedTarget)) {
    dropdownOpen.value = false;
  }
}

// Escape closes the menu and returns focus to its toggle.
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
  auth0.loginWithRedirect();
}
</script>

<style scoped>
/* A button, since it acts rather than links; it keeps the underlined look. */
.nav-logout {
  display: inline;
  padding: 0;
  border: 0;
  background: none;
  font: inherit;
  text-decoration: underline;
}
/* Styled like a small heading, though the user's name isn't one. */
.nav-user-name {
  margin-bottom: 0.5rem;
  font-family: var(--font-heading);
  font-size: 1rem;
  font-weight: 600;
  line-height: 1.2;
}
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
/* An underline that grows from the center on hover and stays on the current
   page, drawn over the label's transparent border. */
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
.router-link-active .nav-label::after {
  transform: scaleX(1);
}
/* Gold hover glow on Log in, like the home cards; keyboard focus keeps its
   focus ring. */
.navbar-nav .btn-primary {
  transition: box-shadow 0.15s ease;
}
.navbar-nav .btn-primary:hover:not(:focus-visible) {
  box-shadow: 0 0 12px color-mix(in srgb, var(--brand-accent) 60%, transparent);
}
/* Gold ring on the profile picture while hovered or while its menu is open. */
#profileDropDown .nav-user-profile {
  transition: box-shadow 0.15s ease;
}
#profileDropDown:hover .nav-user-profile,
#profileDropDown[aria-expanded="true"] .nav-user-profile {
  box-shadow:
    0 0 0 3px color-mix(in srgb, var(--brand-accent) 70%, transparent),
    0 0 10px color-mix(in srgb, var(--brand-accent) 50%, transparent);
}
.router-link-active {
  color: var(--brand-navy);
}
/* The desktop layout; app.css keeps the phone menu until both widths fit. */
@media (min-width: 1200px) and (min-width: 75em) {
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
