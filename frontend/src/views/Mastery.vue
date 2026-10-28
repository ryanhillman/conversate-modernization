<template>
  <RequireProfile>
    <div class="card-style">
      <h1>Mastery</h1>
      <p class="h3">
        You have a mastery of {{ masteryPercent }}% ({{ completedLessons.length }} out of
        {{ LESSONS.length }})
      </p>
      <div class="mastery-bar">
        <div class="mastery-bar-fill" :style="{ width: `${masteryPercent}%` }"></div>
      </div>
    </div>
    <div class="card-style">
      <h2 class="h3">Completed Lessons</h2>
      <ul v-if="completedLessons.length" class="completed-list">
        <li v-for="lesson in completedLessons" :key="lesson.id">
          <span class="completed-check" aria-hidden="true">✓</span> Lesson {{ lesson.id }}:
          <RichText :text="lesson.menuTitle" />
        </li>
      </ul>
      <p v-else>No lessons completed yet.</p>
    </div>
  </RequireProfile>
</template>

<script setup>
import { computed } from "vue";
import RequireProfile from "../components/RequireProfile.vue";
import RichText from "../components/RichText.vue";
import { LESSONS } from "../data/lessons";
import { completedLessonIds } from "../stores/profileStore";

const completedLessons = computed(() =>
  LESSONS.filter((lesson) => completedLessonIds.value.includes(lesson.id)),
);
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

.completed-check {
  color: var(--success-on-dark);
  font-weight: 700;
}

.mastery-bar {
  background: var(--track-on-dark);
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
