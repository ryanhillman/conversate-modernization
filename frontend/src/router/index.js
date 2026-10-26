import { createRouter, createWebHistory } from "vue-router";
import { authGuard } from "@auth0/auth0-vue";
import Home from "../views/Home.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: Home,
      meta: { public: true },
    },
    {
      path: "/mastery",
      name: "mastery",
      meta: { title: "Mastery" },
      component: () => import("../views/Mastery.vue"),
    },
    {
      path: "/profile",
      name: "profile",
      meta: { title: "Profile" },
      component: () => import("../views/Profile.vue"),
    },
    {
      path: "/translate",
      name: "translate",
      meta: { title: "Translate" },
      component: () => import("../views/Translate.vue"),
    },
    {
      path: "/lesson",
      name: "lesson",
      meta: { title: "Lessons" },
      component: () => import("../views/Lesson.vue"),
    },
    {
      path: "/quiz",
      name: "quiz",
      meta: { title: "Quiz" },
      component: () => import("../views/Quiz.vue"),
    },
    {
      path: "/leaderboard",
      name: "leaderboard",
      meta: { title: "Leaderboard" },
      component: () => import("../views/Leaderboard.vue"),
    },
    {
      path: "/:pathMatch(.*)*",
      name: "not-found",
      component: () => import("../views/NotFound.vue"),
      meta: { public: true, title: "Page not found" },
    },
  ],
});

// Fail closed: every route requires authentication unless it opts out with
// meta.public, so a route added later without any annotation is protected by
// default.
router.beforeEach((to) => (to.meta.public ? true : authGuard(to)));

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} | Conversate` : "Conversate";
});

export default router;
