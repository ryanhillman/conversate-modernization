<template>
  <RequireProfile>
    <div v-if="showCelebration" class="celebration">
      <div class="celebration-toast">🎉 Lesson Complete!</div>
      <span v-for="(c, i) in confetti" :key="i" class="confetti-piece" :style="c"></span>
    </div>
    <h1 class="lesson-header">Select any lesson to begin!</h1>

    <div
      v-for="lesson in LESSONS"
      :key="lesson.id"
      class="individual-lesson"
      :class="{ 'is-complete': isComplete(lesson.id) }"
    >
      <span v-if="isComplete(lesson.id)" class="completed-check">
        <span aria-hidden="true">✓</span><span class="visually-hidden">Completed</span>
      </span>
      <div class="lesson-row">
        <!-- A heading per lesson, so screen readers can jump between them. -->
        <h2 class="lesson-name">
          <label :for="lesson.slug" class="lesson-label"
            ><span :id="`${lesson.slug}-title`"><RichText :text="lesson.menuTitle" /></span>:
          </label>
        </h2>
        <!-- Named from its own text plus the title, so the title's Italian keeps
             its lang marking (an aria-label string can't carry it). -->
        <button
          :id="lesson.slug"
          class="lesson-btn toggle-lesson-btn"
          :aria-labelledby="`${lesson.slug}-toggle ${lesson.slug}-title`"
          :aria-expanded="currentLessonId === lesson.id ? 'true' : 'false'"
          @click="selectLesson(lesson.id)"
        >
          <span :id="`${lesson.slug}-toggle`">Toggle lesson</span>
        </button>
      </div>

      <div v-if="currentLessonId === lesson.id" class="lesson-content">
        <h3 class="h1">Lesson {{ lesson.id }}: <RichText :text="lesson.title" /></h3>

        <template v-for="(s, si) in lesson.sections">
          <!-- level places it in the outline under the lesson title; size is
               only how big it looks. -->
          <component
            :is="'h' + (s.level + 3)"
            v-if="s.t === 'h'"
            :key="'s' + si"
            :class="'h' + s.size"
          >
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
              <button type="button" class="speakable" lang="it" @click="speak(r[1])">
                <span class="visually-hidden" lang="en">Play</span> {{ r[1] }}
              </button>
              — {{ r[2] }}
            </li>
          </ul>
        </template>

        <template v-if="lesson.questions.length">
          <h4 class="h5">Now let's practice some on your own!</h4>
          <p v-if="lesson.practiceInstructions"><RichText :text="lesson.practiceInstructions" /></p>
          <div v-for="question in lesson.questions" :key="question.id">
            <label :for="question.id" class="question-label"
              ><RichText :text="question.prompt"
            /></label>
            <span class="answer-field" :class="answerState(question)">
              <input
                :id="question.id"
                v-model.trim="answers[question.id]"
                :name="question.id"
                type="text"
                :lang="lesson.answerLang"
                class="answer-input"
                :aria-invalid="answerState(question) === 'wrong' ? 'true' : undefined"
                @input="submitted[question.id] = false"
                @keydown.enter="submitAnswer(question)"
                @blur="submitAnswer(question)"
              />
            </span>
          </div>
        </template>
        <div v-else-if="!isComplete(lesson.id)" class="complete-lesson">
          <button
            class="lesson-btn"
            :aria-disabled="completing"
            @click="completeWithButton(lesson)"
          >
            Mark lesson complete
          </button>
        </div>
      </div>
    </div>
  </RequireProfile>
</template>

<script setup>
import { ref, reactive, computed, nextTick } from "vue";
import { completeLesson } from "../api/users";
import { generateConfetti } from "../utils/confetti";
import RequireProfile from "../components/RequireProfile.vue";
import RichText from "../components/RichText.vue";
import { LESSONS } from "../data/lessons";
import { isAnswerCorrect, isLessonComplete, normalizeAnswer } from "../utils/grading";
import { synthesizeSpeech } from "../api/tts";
import { completedLessonIds, setProfile } from "../stores/profileStore";
import { announce } from "../stores/announceStore";
import { showToast } from "../stores/toastStore";

const answers = reactive({});
// Answers are marked right or wrong once submitted (Enter or leaving the box),
// not while typing.
const submitted = reactive({});
LESSONS.forEach((lesson) =>
  lesson.questions.forEach((q) => {
    answers[q.id] = "";
    submitted[q.id] = false;
  }),
);

const currentLessonId = ref(null);
const showCelebration = ref(false);
const confetti = ref([]);
const completing = ref(false);

const currentLesson = computed(
  () => LESSONS.find((lesson) => lesson.id === currentLessonId.value) || null,
);

function selectLesson(lessonId) {
  currentLessonId.value = currentLessonId.value === lessonId ? null : lessonId;
}
function isAnswered(question) {
  return normalizeAnswer(answers[question.id]) !== "";
}
function isCorrect(question) {
  return isAnswerCorrect(answers[question.id], question.correctAnswers);
}
// "correct" or "wrong" once an answer is submitted, otherwise null.
function answerState(question) {
  if (!submitted[question.id] || !isAnswered(question)) return null;
  return isCorrect(question) ? "correct" : "wrong";
}
function submitAnswer(question) {
  // Enter followed by leaving the box submits twice; only announce the first.
  if (!submitted[question.id] && isAnswered(question)) {
    announce(isCorrect(question) ? "Correct" : "Incorrect");
  }
  submitted[question.id] = true;
  checkCurrentLesson();
}
function checkCurrentLesson() {
  const lesson = currentLesson.value;
  if (lesson && isLessonComplete(lesson.questions, answers)) {
    markLessonComplete(lesson.id);
  }
}
function isComplete(lessonId) {
  return completedLessonIds.value.includes(lessonId);
}
// The button disappears once the lesson is done, so move focus to its Toggle.
async function completeWithButton(lesson) {
  await markLessonComplete(lesson.id);
  if (isComplete(lesson.id)) {
    await nextTick();
    document.getElementById(lesson.slug)?.focus();
  }
}
async function markLessonComplete(lessonId) {
  if (completing.value) return;
  if (!isComplete(lessonId)) {
    completing.value = true;
    try {
      const data = await completeLesson(lessonId);
      setProfile(data);
      launchCelebration();
      announce("Lesson complete!");
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
</script>

<style scoped>
/* The navy, amber-on-hover buttons used throughout the lessons. */
.lesson-btn {
  padding: 0.5em 2em;
  border: none;
  border-radius: 8px;
  margin: 0 0.3em 0.3em 0;
  box-sizing: border-box;
  text-decoration: none;
  font-family: "Poppins", sans-serif;
  font-weight: 500;
  color: var(--text-on-dark);
  background-color: var(--brand-navy);
  text-align: center;
  transition: all 0.25s;
}
.lesson-btn:hover {
  background-color: var(--brand-accent);
  color: var(--text-color);
}
.lesson-btn[aria-disabled="true"] {
  opacity: 0.65;
}
@media all and (max-width: 30em) {
  .lesson-btn {
    display: block;
    margin: 0.4em auto;
  }
}
.individual-lesson {
  position: relative;
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
/* A heading, styled as plain text. */
.lesson-header {
  font-family: inherit;
  font-size: 1rem;
  font-weight: 400;
  line-height: 1.5;
  color: var(--text-on-dark);
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
.lesson-content {
  margin-top: 1.5rem;
}
.question-label {
  margin-right: 0.75rem;
}
/* An input can't have ::after, so the check or X is drawn on this wrapper. */
.answer-field {
  position: relative;
  display: inline-block;
  max-width: 100%;
  margin: 2rem auto;
}
.answer-input {
  border-radius: 12px;
  box-shadow: var(--card-shadow);
  padding: 1rem;
  max-width: 100%;
}
.complete-lesson {
  text-align: center;
  margin-top: 1.5rem;
}
.complete-lesson .lesson-btn {
  margin-left: 0;
}
.answer-field.correct .answer-input {
  border: 2px solid var(--success);
  border-radius: 20px;
  background-color: var(--success-bg);
}
.answer-field.wrong .answer-input {
  border: 2px solid var(--danger-text);
  border-radius: 20px;
  background-color: var(--bs-danger-bg-subtle);
}
.answer-field.correct {
  animation: correctPop 0.3s ease;
}
/* The SVG supplies only the shape; the color comes from the token. */
.answer-field.correct::after,
.answer-field.wrong::after {
  content: "";
  position: absolute;
  top: 50%;
  right: calc(0.75rem + 2px);
  width: 1.1rem;
  height: 1.1rem;
  transform: translateY(-50%);
  mask: no-repeat center / contain;
  pointer-events: none;
}
.answer-field.correct::after {
  background-color: var(--success);
  mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z'/%3E%3C/svg%3E");
}
.answer-field.wrong::after {
  background-color: var(--danger-text);
  mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z'/%3E%3C/svg%3E");
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
  border: 0;
  font: inherit;
  color: var(--brand-navy);
  font-weight: 700;
  background-color: color-mix(in srgb, var(--brand-accent) 18%, transparent);
  border-radius: 6px;
  border-bottom: 2px solid var(--brand-accent-dark);
  padding: 0.05em 0.5em;
  cursor: pointer;
  transition:
    background-color 0.15s,
    color 0.15s;
}
.speakable:hover {
  background-color: color-mix(in srgb, var(--brand-accent) 32%, transparent);
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
  color: var(--text-on-dark);
  padding: 0.9rem 2rem;
  border-radius: 999px;
  font-family: "Poppins", sans-serif;
  font-weight: 600;
  font-size: 1.1rem;
  box-shadow: var(--popup-shadow);
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
/* Completed lessons: a corner check, and a green title and Toggle (5.14:1
   with white text). Toggle keeps its amber hover. */
.completed-check {
  position: absolute;
  top: -0.75rem;
  right: -0.75rem;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background-color: var(--success);
  color: var(--text-on-dark);
  font-weight: 700;
  box-shadow: var(--card-shadow);
}
.is-complete .lesson-label,
.is-complete .toggle-lesson-btn:not(:hover) {
  background-color: var(--success);
}
/* Title and Toggle on one row, wrapping on narrow screens. */
.lesson-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}
.lesson-row .lesson-label {
  display: block;
  margin: 0;
}
/* A heading for structure only; the label inside it keeps its look. */
.lesson-name {
  font: inherit;
  margin: 0;
}
.toggle-lesson-btn {
  margin: 0;
  padding: 1rem;
}
.lesson-label {
  border-radius: 12px;
  box-shadow: var(--card-shadow);
  padding: 1rem;
  margin: 1rem auto;
  max-width: 40rem;
  color: var(--text-on-dark);
  background-color: var(--brand-navy);
}
</style>
