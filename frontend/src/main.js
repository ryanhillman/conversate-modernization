// Must stay above App.vue: component styles have to be emitted last.
import "bootstrap/dist/css/bootstrap.min.css";
import "./assets/app.css";

import { createApp, reactive, computed } from "vue";
import App from "./App.vue";
import router from "./router";
import { auth0 } from "./auth";

const app = createApp(App);
app.use(router);
app.use(auth0);

app.config.globalProperties.$auth = reactive({
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

app.mount("#app");
