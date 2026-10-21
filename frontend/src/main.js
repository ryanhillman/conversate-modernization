// Must stay above App.vue: component styles have to be emitted last.
import "bootstrap/dist/css/bootstrap.min.css";
import "./assets/app.css";

import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import { auth0 } from "./auth";
import { useAuth } from "./composables/useAuth";

const app = createApp(App);
app.use(router);
app.use(auth0);

app.config.globalProperties.$auth = useAuth();

app.mount("#app");
