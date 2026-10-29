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

// Each page's code and CSS are separate files named for their build, so after
// a deploy a page left open asks for a file that's gone. Load the new build at
// that address instead, once: if the file is still missing, the error stands.
const STALE_FILE =
  /dynamically imported module|Importing a module script failed|Unable to preload CSS/i;
const RELOAD_KEY = "reloadedForMissingFile";

export function reloadOnMissingFile(error, to, reload = (path) => window.location.assign(path)) {
  if (!STALE_FILE.test(error?.message ?? "")) return false;
  try {
    if (sessionStorage.getItem(RELOAD_KEY) === to.fullPath) return false;
    sessionStorage.setItem(RELOAD_KEY, to.fullPath);
  } catch {
    // Without storage there's no way to stop a reload loop, so don't start one.
    return false;
  }
  reload(to.fullPath);
  return true;
}

router.onError((error, to) => reloadOnMissingFile(error, to));

router.afterEach((to, from, failure) => {
  // A page that loaded resets the one-reload guard above.
  if (!failure) {
    try {
      sessionStorage.removeItem(RELOAD_KEY);
    } catch {
      // Nothing to reset without storage.
    }
  }
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
