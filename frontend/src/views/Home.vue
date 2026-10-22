<template>
  <div class="text-center">
    <div class="card-style welcome-card">
      <h1>Welcome to Conversate!</h1>
    </div>
    <div class="cards">
      <div class="card" v-for="card in cards" :key="card.to">
        <img class="card-img-top" :src="card.img" :alt="card.alt" />
        <div class="card-body">
          <router-link :to="card.to" class="btn btn-primary">{{ card.label }}</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const cards = [
  { img: "/profile.png", alt: "Profile", to: "/profile", label: "Profile" },
  { img: "/mastery.png", alt: "Mastery", to: "/mastery", label: "Mastery" },
  { img: "/study.png", alt: "Learn", to: "/lesson", label: "Lessons" },
  { img: "/translate.png", alt: "Translate", to: "/translate", label: "Translate" },
  { img: "/quiz.png", alt: "Quiz", to: "/quiz", label: "Quiz" },
  { img: "/leaderboard.png", alt: "Leaderboard", to: "/leaderboard", label: "Leaderboard" },
];
</script>

<style scoped>
.welcome-card {
  width: fit-content;
  max-width: 95vw;
}
.welcome-card h1 {
  margin: 0;
}
.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(10.5rem, 1fr));
  gap: 1rem;
  padding: 1rem 0;
  width: 100%;
}
.cards > .card {
  margin: 0;
  border-radius: 12px;
  box-shadow: var(--card-shadow);
  border-top: 4px solid var(--brand-accent);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.card-img-top {
  height: 10rem;
  width: 100%;
  object-fit: cover;
}
.card-body {
  padding: 1.25rem 0.75rem;
}
.card:hover {
  transform: translateY(-6px);
}
.card .btn-primary {
  display: block;
  width: 100%;
  padding: 0.4rem 0.4rem;
  white-space: normal;
  background-color: var(--brand-accent);
  border-color: var(--brand-accent);
  color: var(--text-color);
}
.card .btn-primary:hover {
  background-color: var(--brand-accent-dark);
  border-color: var(--brand-accent-dark);
}
</style>
