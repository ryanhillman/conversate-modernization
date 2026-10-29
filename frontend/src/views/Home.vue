<template>
  <div class="text-center">
    <div class="card-style welcome-card" :class="{ 'welcome-shine': shine }">
      <h1>Welcome to Conversate!</h1>
    </div>
    <div class="cards">
      <div v-for="card in cards" :key="card.path" class="card">
        <!-- Decorative: the button below names the page. -->
        <img class="card-img-top" :src="card.img" alt="" />
        <div class="card-body">
          <router-link :to="card.path" class="btn btn-accent">{{ card.label }}</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { pages } from "../router/pages";

const cards = pages.filter((page) => page.img);

// The welcome's light sweep plays the first time Home appears in a browser
// session. Without session storage (some private modes), it plays every time.
let shine = true;
try {
  shine = !sessionStorage.getItem("welcomeShinePlayed");
  sessionStorage.setItem("welcomeShinePlayed", "1");
} catch {
  // Keep shine on.
}
</script>

<style scoped>
.welcome-card {
  width: fit-content;
  max-width: 95vw;
}
.welcome-card h1 {
  margin: 0;
}
/* A light band sweeps across the welcome once as the page loads, through the
   background so nothing is clipped. Instant for reduced motion (app.css). */
.welcome-shine {
  background-image: linear-gradient(
    105deg,
    transparent 35%,
    color-mix(in srgb, var(--text-on-dark) 22%, transparent) 50%,
    transparent 65%
  );
  background-size: 300% 100%;
  background-repeat: no-repeat;
  animation: welcome-shine 1.4s ease-in-out 0.2s both;
}
@keyframes welcome-shine {
  from {
    background-position: 105% 0;
  }
  to {
    background-position: -5% 0;
  }
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
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}
.card-img-top {
  height: 10rem;
  width: 100%;
  object-fit: contain;
  padding: 1rem;
}
.card-body {
  padding: 1.25rem 0.75rem;
}
.card:hover,
.card:focus-within {
  transform: translateY(-6px);
  box-shadow:
    var(--card-shadow),
    0 0 18px color-mix(in srgb, var(--brand-accent) 55%, transparent);
}
.card .btn {
  display: block;
  width: 100%;
  padding: 0.4rem 0.4rem;
  white-space: normal;
}
</style>
