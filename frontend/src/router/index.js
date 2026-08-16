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
      component: () => import("../views/Mastery.vue"),
    },
    {
      path: "/profile",
      name: "profile",
      component: () => import("../views/Profile.vue"),
    },
    {
      path: "/translate",
      name: "translate",
      component: () => import("../views/Translate.vue"),
    },
    {
      path: "/lesson",
      name: "lesson",
      component: () => import("../views/Lesson.vue"),
    },
    {
      path: "/quiz",
      name: "quiz",
      component: () => import("../views/Quiz.vue"),
    },
    {
      path: "/leaderboard",
      name: "leaderboard",
      component: () => import("../views/Leaderboard.vue"),
    },
    {
      path: "/:pathMatch(.*)*",
      name: "not-found",
      component: () => import("../views/NotFound.vue"),
      meta: { public: true },
    },
  ],
});

// Fail closed: every route requires authentication unless it opts out with
// meta.public, so a route added later without any annotation is protected by
// default.
router.beforeEach((to) => (to.meta.public ? true : authGuard(to)));

export default router;
