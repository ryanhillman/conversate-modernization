<template>
  <RequireProfile @loaded="user = $event">
    <div class="card-style">
      <h1>Mastery</h1>
      <h3>
        You have a mastery of {{ masteryPercent }}% ({{ completedLessons.length }}
        out of {{ LESSONS.length }})
      </h3>
      <div class="mastery-bar">
        <div class="mastery-bar-fill" :style="{ width: masteryPercent + '%' }"></div>
      </div>
    </div>
    <div class="card-style">
      <h3>Completed Lessons</h3>
      <ul v-if="completedLessons.length" class="completed-list">
        <li v-for="lesson in completedLessons" :key="lesson.id">
          ✓ Lesson {{ lesson.id }}: {{ lesson.menuTitle }}
        </li>
      </ul>
      <p v-else>No lessons completed yet.</p>
    </div>
  </RequireProfile>
</template>

<script setup>
import { ref, computed } from "vue";
import RequireProfile from "../components/RequireProfile.vue";
import { LESSONS } from "../data/lessons.js";

const user = ref(null);

const completedLessons = computed(() => {
  const completed = (user.value && user.value.lessons_completed) || [];
  return LESSONS.filter((lesson) => completed.includes(lesson.id));
});
const masteryPercent = computed(() =>
  Math.round((completedLessons.value.length / LESSONS.length) * 100),
);
</script>

<style scoped>
.completed-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.completed-list li {
  padding: 0.25rem 0;
}

.mastery-bar {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 999px;
  height: 14px;
  max-width: 28rem;
  margin: 0.75rem auto 0;
  overflow: hidden;
}

.mastery-bar-fill {
  background: var(--brand-accent);
  height: 100%;
  border-radius: 999px;
  transform-origin: left;
  animation: masteryFill 0.5s ease;
}

@keyframes masteryFill {
  from {
    transform: scaleX(0);
  }

  to {
    transform: scaleX(1);
  }
}
</style>