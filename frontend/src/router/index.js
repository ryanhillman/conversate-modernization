import { createRouter, createWebHistory } from "vue-router";
import { authGuard } from "@auth0/auth0-vue";
import { clearErrorToasts } from "../stores/toastStore";
import { pageTitle } from "../utils/pageTitle";
import Home from "../views/Home.vue";
import { pages } from "./pages";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: Home,
      meta: { public: true },
    },
    ...pages
      .filter((page) => page.view)
      .map((page) => ({
        path: page.path,
        name: page.path.slice(1),
        meta: { title: page.label },
        component: page.view,
      })),
    {
      path: "/:pathMatch(.*)*",
      name: "not-found",
      component: () => import("../views/NotFound.vue"),
      meta: { public: true, title: "Page not found" },
    },
  ],
});

// Fail closed: every route needs a login unless it sets meta.public.
router.beforeEach((to) => (to.meta.public ? true : authGuard(to)));

router.afterEach((to, from) => {
  if (to.path !== from.path) {
    // An error toast is about the page it appeared on.
    clearErrorToasts();
    // The old page, and whatever had focus on it, is gone; start at the new
    // page's content. Not on the first load.
    if (from.matched.length) document.getElementById("main")?.focus();
  }
  document.title = pageTitle(to.meta.title);
});

export default router;
