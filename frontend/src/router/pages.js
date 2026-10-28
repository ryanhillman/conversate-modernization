// The nav bar's pages, in order. Those with an image also get a card on the
// home page; view is loaded on the first visit.
export const pages = [
  { path: "/", label: "Home" },
  {
    path: "/profile",
    label: "Profile",
    img: "/profile.webp",
    view: () => import("../views/Profile.vue"),
  },
  {
    path: "/mastery",
    label: "Mastery",
    img: "/mastery.webp",
    view: () => import("../views/Mastery.vue"),
  },
  {
    path: "/lesson",
    label: "Lessons",
    img: "/study.webp",
    view: () => import("../views/Lesson.vue"),
  },
  {
    path: "/translate",
    label: "Translate",
    img: "/translate.webp",
    view: () => import("../views/Translate.vue"),
  },
  {
    path: "/quiz",
    label: "Quiz",
    img: "/quiz.webp",
    view: () => import("../views/Quiz.vue"),
  },
  {
    path: "/leaderboard",
    label: "Leaderboard",
    img: "/leaderboard.webp",
    view: () => import("../views/Leaderboard.vue"),
  },
];
