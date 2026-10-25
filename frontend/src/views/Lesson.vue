<template>
  <RequireProfile>
    <div v-if="showCelebration" class="celebration">
      <div class="celebration-toast">🎉 Lesson Complete!</div>
      <span v-for="(c, i) in confetti" :key="i" class="confetti-piece" :style="c"></span>
    </div>
    <header class="lesson-header">Select any lesson to begin!</header>

    <div v-for="lesson in lessons" :key="lesson.id" class="individual-lesson">
      <label :for="lesson.slug" class="lesson-label">{{ lesson.menuTitle }}: </label>
      <button :id="lesson.slug" class="toggle-lesson-btn" @click="selectLesson(lesson.id)">
        Toggle lesson
      </button>
      <span v-if="isComplete(lesson.id)" class="completed-badge">✓ Completed</span>

      <div v-if="currentLessonId === lesson.id">
        <h1>Lesson {{ lesson.id }}: <RichText :text="lesson.title" /></h1>

        <template v-for="(s, si) in lesson.sections">
          <component v-if="s.t === 'h'" :is="'h' + s.lvl" :key="'s' + si">
            <RichText :text="s.html" />
          </component>
          <p v-else-if="s.t === 'p'" :key="'s' + si"><RichText :text="s.html" /></p>
          <ul v-else-if="s.t === 'ul'" :key="'s' + si">
            <li v-for="(it, ii) in s.items" :key="ii"><RichText :text="it" /></li>
          </ul>
          <ul v-else-if="s.t === 'conj'" :key="'s' + si">
            <li v-for="(r, ri) in s.rows" :key="ri">
              <span lang="it">{{ r[0] }}</span
              >:
              <span
                class="speakable"
                lang="it"
                role="button"
                tabindex="0"
                @click="speak(r[1])"
                @keydown.enter="speak(r[1])"
                @keydown.space.prevent="speak(r[1])"
                >{{ r[1] }}</span
              >
              — {{ r[2] }}
            </li>
          </ul>
        </template>

        <template v-if="lesson.questions.length">
          <h5>Now let's practice some on your own!</h5>
          <div v-for="question in lesson.questions" :key="question.id">
            <label :for="question.id">{{ question.prompt }}</label>
            <input
              :id="question.id"
              :name="question.id"
              type="text"
              lang="it"
              class="answer-input"
              v-model.trim="answers[question.id]"
              :class="{
                correct: isCorrect(question),
                wrong: isAnswered(question) && !isCorrect(question),
              }"
            />
          </div>
        </template>
        <div v-else-if="!isComplete(lesson.id)" class="complete-lesson">
          <!-- Navy comes from this view's scoped `button` style, which overrides btn-success -->
          <button
            class="btn btn-success"
            :disabled="completing"
            @click="markLessonComplete(lesson.id)"
          >
            Mark lesson complete
          </button>
        </div>
      </div>
    </div>
  </RequireProfile>
</template>

<script setup>
import { ref, reactive, computed, watch } from "vue";
import { completeLesson } from "../api/users";
import { generateConfetti } from "../utils/confetti";
import RequireProfile from "../components/RequireProfile.vue";
import RichText from "../components/RichText.vue";
import { LESSONS } from "../data/lessons";
import { synthesizeSpeech } from "../api/tts";
import { profile as user, setProfile } from "../stores/profileStore";
import { showToast } from "../stores/toastStore";

const lessons = LESSONS;

const answers = reactive({});
LESSONS.forEach((lesson) =>
  lesson.questions.forEach((q) => {
    answers[q.id] = "";
  }),
);

const currentLessonId = ref(null);
const showCelebration = ref(false);
const confetti = ref([]);
const completing = ref(false);

const currentLesson = computed(
  () => lessons.find((lesson) => lesson.id === currentLessonId.value) || null,
);

function selectLesson(lessonId) {
  currentLessonId.value = currentLessonId.value === lessonId ? null : lessonId;
}
function normalize(value) {
  return (value || "").trim().toLowerCase();
}
function isAnswered(question) {
  return normalize(answers[question.id]) !== "";
}
function isCorrect(question) {
  const value = normalize(answers[question.id]);
  return value !== "" && question.correctAnswers.some((a) => normalize(a) === value);
}
function checkAnswers(lesson) {
  return lesson.questions.length > 0 && lesson.questions.every((q) => isCorrect(q));
}
function checkCurrentLesson() {
  const lesson = currentLesson.value;
  if (lesson && checkAnswers(lesson)) {
    markLessonComplete(lesson.id);
  }
}
function isComplete(lessonId) {
  const completed = user.value && user.value.lessons_completed ? user.value.lessons_completed : [];
  return completed.includes(lessonId);
}
async function markLessonComplete(lessonId) {
  if (completing.value) return;
  const completed = user.value && user.value.lessons_completed ? user.value.lessons_completed : [];
  if (!completed.includes(lessonId)) {
    completing.value = true;
    try {
      const data = await completeLesson(lessonId);
      setProfile(data);
      launchCelebration();
    } catch (err) {
      console.error("Failed to save lesson completion:", err);
      showToast("Could not save your progress.", "error");
    } finally {
      completing.value = false;
    }
  }
}
async function speak(text) {
  try {
    const { audio_content } = await synthesizeSpeech(text, "it");
    await new Audio(`data:audio/mpeg;base64,${audio_content}`).play();
  } catch (err) {
    console.error("Speech synthesis failed:", err);
    showToast("Could not play audio.", "error");
  }
}
function launchCelebration() {
  confetti.value = generateConfetti();
  showCelebration.value = true;
  setTimeout(() => {
    showCelebration.value = false;
  }, 3200);
}

watch(answers, () => {
  checkCurrentLesson();
});
</script>

<style scoped>
.individual-lesson {
  border-radius: var(--radius);
  box-shadow: var(--card-shadow);
  border: var(--card-border);
  padding: 1.5rem;
  margin: 2rem auto;
  max-width: 40rem;
  background-color: var(--card-bg);
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}
.individual-lesson:hover {
  transform: translateY(-3px);
}
.lesson-header {
  color: #fff;
  padding-top: 2.5rem;
  padding-bottom: 2.5rem;
  background-color: var(--brand-navy);
  text-align: center;
  border-radius: var(--radius);
  box-shadow: var(--card-shadow);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  max-width: 40rem;
  margin: auto;
}
.answer-input {
  border-radius: 12px;
  box-shadow: var(--card-shadow);
  padding: 1rem;
  margin: 2rem auto;
  max-width: 40rem;
}
.complete-lesson {
  text-align: center;
  margin-top: 1.5rem;
}
.complete-lesson button {
  margin-left: 0;
}
.wrong {
  border-color: red;
  border-radius: 20px;
}
.correct {
  border: 2px solid #1e7e34;
  border-radius: 20px;
  background-color: #e9f9ec;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%231e7e34'%3E%3Cpath d='M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 1.1rem;
  animation: correctPop 0.3s ease;
}
@keyframes correctPop {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.04);
  }
  100% {
    transform: scale(1);
  }
}
.speakable {
  display: inline-block;
  color: var(--brand-navy);
  font-weight: 700;
  background-color: rgba(224, 168, 46, 0.18);
  border-radius: 6px;
  border-bottom: 2px solid var(--brand-accent-dark);
  padding: 0.05em 0.5em;
  cursor: pointer;
  transition:
    background-color 0.15s,
    color 0.15s;
}
.speakable:hover {
  background-color: rgba(224, 168, 46, 0.32);
  color: var(--brand-navy);
}
.celebration {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 1000;
  overflow: hidden;
}
.confetti-piece {
  position: fixed;
  top: -16px;
  width: 9px;
  height: 14px;
  border-radius: 2px;
  animation-name: confettiFall;
  animation-timing-function: linear;
  animation-fill-mode: forwards;
}
@keyframes confettiFall {
  to {
    top: 105vh;
    opacity: 0.7;
  }
}
.celebration-toast {
  position: fixed;
  top: 2rem;
  left: 50%;
  transform: translateX(-50%);
  background: var(--brand-navy);
  color: #fff;
  padding: 0.9rem 2rem;
  border-radius: 999px;
  font-family: "Poppins", sans-serif;
  font-weight: 600;
  font-size: 1.1rem;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
  animation:
    toastIn 0.4s ease,
    toastOut 0.4s ease 2.7s forwards;
}
@keyframes toastIn {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}
@keyframes toastOut {
  to {
    opacity: 0;
    transform: translateX(-50%) translateY(-20px);
  }
}
.completed-badge {
  display: inline-block;
  margin-left: 1rem;
  padding: 0.3rem 0.8rem;
  border-radius: 12px;
  background-color: #1e7e34;
  color: white;
  font-weight: 600;
  font-size: 0.9rem;
}
.toggle-lesson-btn {
  margin-left: 75%;
  padding: 1rem;
}
.lesson-label {
  border-radius: 12px;
  box-shadow: var(--card-shadow);
  padding: 1rem;
  margin: 1rem auto;
  max-width: 40rem;
  color: white;
  background-color: var(--brand-navy);
}
button {
  padding: 0.5em 2em;
  border: none;
  border-radius: 8px;
  margin: 0 0.3em 0.3em 0;
  box-sizing: border-box;
  text-decoration: none;
  font-family: "Poppins", sans-serif;
  font-weight: 500;
  color: white;
  background-color: var(--brand-navy);
  text-align: center;
  transition: all 0.25s;
}
button:hover {
  background-color: var(--brand-accent);
  color: var(--text-color);
}
@media all and (max-width: 30em) {
  button {
    display: block;
    margin: 0.4em auto;
  }
}
</style>
