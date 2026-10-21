import { reactive, computed } from "vue";
import { auth0 } from "../auth";

// Singleton so every caller (main.js's $auth global property and any
// component's script) shares one reactive object instead of recomputing it.
let authState = null;

export function useAuth() {
  if (!authState) {
    authState = reactive({
      isAuthenticated: computed(() => auth0.isAuthenticated.value),
      loading: computed(() => auth0.isLoading.value),
      user: computed(() => auth0.user.value ?? {}),
      error: computed(() => auth0.error.value),
      loginWithRedirect: () => auth0.loginWithRedirect(),
      logout: () =>
        auth0.logout({
          logoutParams: { returnTo: window.location.origin },
        }),
    });
  }
  return authState;
}
