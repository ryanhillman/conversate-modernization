<template>
  <div class="not-found">
    <h1>404</h1>
    <p>We couldn't find that page.</p>
    <router-link class="btn btn-success" to="/">Back to home</router-link>
  </div>
</template>

<style scoped>
.not-found {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  margin: 4rem auto;
}
.not-found h1 {
  font-size: 4rem;
  margin-bottom: 0.5rem;
}
.not-found p {
  margin-bottom: 1.5rem;
}
</style>
