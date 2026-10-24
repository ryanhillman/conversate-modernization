<template>
  <RequireProfile>
    <div class="text-center">
      <div class="card-style">
        <h2>Quiz</h2>
      </div>

      <div v-if="phase === 'ready'" class="card-style quiz-results">
        <button class="btn btn-accent m-2" @click="start">Start Quiz</button>
      </div>

      <div v-else-if="phase === 'loading'" class="loading-state">
        <p>Loading…</p>
      </div>

      <div v-else-if="phase === 'active' || phase === 'paused'" class="quiz-card-wrap">
        <div class="quiz-meta">
          <span>Question {{ currentIndex + 1 }} / {{ questions.length }}</span>
          <span class="quiz-timer">{{ formattedRemaining }}</span>
          <span class="quiz-pauses">Pauses left: {{ pausesRemaining }}</span>
          <button
            v-if="phase === 'active' && pausesRemaining > 0"
            class="btn btn-sm btn-outline-primary"
            :disabled="advancing"
            @click="pause"
          >
            Pause
          </button>
          <button v-else-if="phase === 'paused'" class="btn btn-sm btn-accent" @click="resume">
            Resume
          </button>
        </div>

        <div v-if="phase === 'paused'" class="quiz-card quiz-paused">
          <p>Paused</p>
          <button class="btn btn-accent" @click="resume">Resume</button>
        </div>
        <transition v-else name="card-flip" mode="out-in">
          <div class="quiz-card" :key="currentIndex">
            <h3 class="quiz-word">{{ currentQuestion.it }}</h3>
            <div class="quiz-choices">
              <button
                v-for="choice in currentQuestion.choices"
                :key="choice"
                class="btn btn-outline-primary quiz-choice"
                :class="choiceClass(choice)"
                :disabled="advancing"
                @click="selectAnswer(choice)"
              >
                {{ choice }}
              </button>
            </div>
          </div>
        </transition>
      </div>

      <div v-else-if="phase === 'results'" class="card-style quiz-results">
        <h3 v-if="result.is_new_best">New best!</h3>
        <p>Score: {{ result.score }} / {{ questions.length }}</p>
        <p>Time: {{ formatTime(result.time_seconds) }}</p>
        <button class="btn btn-accent m-2" @click="start">Play again</button>
        <router-link to="/leaderboard" class="btn btn-accent m-2"> View leaderboard </router-link>
      </div>

      <div v-else-if="phase === 'error'" class="card-style">
        <p>Could not load the quiz.</p>
        <button class="btn btn-accent" @click="start">Try again</button>
      </div>
    </div>
  </RequireProfile>
</template>

<script setup>
import { ref, computed, onBeforeUnmount } from "vue";
import RequireProfile from "../components/RequireProfile.vue";
import { startQuiz, answerQuiz, pauseQuiz, resumeQuiz, submitQuiz } from "../api/quiz";
import { showToast } from "../stores/toastStore";
import { formatTime } from "../utils/formatTime";

const FEEDBACK_DISPLAY_MS = 500;

const phase = ref("ready");
const questions = ref([]);
const currentIndex = ref(0);
const result = ref(null);
const advancing = ref(false);
const selectedChoice = ref(null);
const feedback = ref(null);
const displayStart = ref(0);
const secondsRemainingAtStart = ref(0);
const remainingSeconds = ref(0);
const pausesRemaining = ref(0);
let tickTimer = null;

const currentQuestion = computed(() => questions.value[currentIndex.value]);
const formattedRemaining = computed(() => formatTime(remainingSeconds.value));

onBeforeUnmount(() => clearInterval(tickTimer));

function choiceClass(choice) {
  if (choice !== selectedChoice.value || !feedback.value) return "";
  return feedback.value === "correct" ? "quiz-choice-correct" : "quiz-choice-wrong";
}

function resetDisplayClock(secondsRemaining) {
  displayStart.value = Date.now();
  secondsRemainingAtStart.value = secondsRemaining;
  remainingSeconds.value = secondsRemaining;
}

function tick() {
  const elapsed = Math.floor((Date.now() - displayStart.value) / 1000);
  remainingSeconds.value = Math.max(0, secondsRemainingAtStart.value - elapsed);
  if (remainingSeconds.value === 0) {
    finish();
  }
}

async function start() {
  clearInterval(tickTimer);
  phase.value = "loading";
  try {
    const data = await startQuiz();
    resetDisplayClock(data.seconds_remaining);
    questions.value = data.questions;
    currentIndex.value = 0;
    advancing.value = false;
    selectedChoice.value = null;
    feedback.value = null;
    pausesRemaining.value = data.pauses_remaining;
    phase.value = "active";
    tickTimer = setInterval(tick, 1000);
  } catch (err) {
    console.error("Failed to start quiz:", err);
    phase.value = "error";
  }
}

async function pause() {
  if (phase.value !== "active") return;
  try {
    const data = await pauseQuiz();
    clearInterval(tickTimer);
    phase.value = "paused";
    remainingSeconds.value = data.seconds_remaining;
    pausesRemaining.value = data.pauses_remaining;
  } catch (err) {
    console.error("Failed to pause quiz:", err);
    showToast("Could not pause the quiz.", "error");
  }
}

async function resume() {
  if (phase.value !== "paused") return;
  try {
    const data = await resumeQuiz();
    resetDisplayClock(data.seconds_remaining);
    pausesRemaining.value = data.pauses_remaining;
    phase.value = "active";
    tickTimer = setInterval(tick, 1000);
  } catch (err) {
    console.error("Failed to resume quiz:", err);
    showToast("Could not resume the quiz.", "error");
  }
}

async function selectAnswer(choice) {
  if (advancing.value) return;
  advancing.value = true;
  selectedChoice.value = choice;
  try {
    const { correct } = await answerQuiz(currentIndex.value, choice);
    feedback.value = correct ? "correct" : "wrong";
  } catch (err) {
    console.error("Failed to submit answer:", err);
    if (err.status === 409) {
      // Time ran out server-side between clicking and this request landing,
      // or the question is out of sync. Finalize with whatever's been
      // graded so far instead of leaving the user stuck on a dead question.
      finish();
      return;
    }
    // A network blip or server error shouldn't end the quiz — let the user
    // retry the same question.
    showToast("Could not submit your answer. Try again.", "error");
    selectedChoice.value = null;
    advancing.value = false;
    return;
  }
  setTimeout(() => {
    selectedChoice.value = null;
    feedback.value = null;
    if (currentIndex.value < questions.value.length - 1) {
      currentIndex.value += 1;
      advancing.value = false;
    } else {
      finish();
    }
  }, FEEDBACK_DISPLAY_MS);
}

async function finish() {
  if (phase.value !== "active" && phase.value !== "paused") return;
  clearInterval(tickTimer);
  phase.value = "loading";
  try {
    result.value = await submitQuiz();
    phase.value = "results";
  } catch (err) {
    console.error("Failed to submit quiz:", err);
    showToast("Could not submit your quiz result.", "error");
    phase.value = "error";
  }
}
</script>

<style scoped>
.quiz-card-wrap {
  max-width: 40rem;
  margin: 0 auto;
}
.quiz-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 1rem;
}
.quiz-timer {
  font-variant-numeric: tabular-nums;
}
.quiz-card {
  border-radius: var(--radius);
  box-shadow: var(--card-shadow);
  border: var(--card-border);
  background-color: var(--card-bg);
  padding: 2.5rem 1.5rem;
}
.quiz-paused {
  color: var(--text-muted);
}
.quiz-word {
  margin-bottom: 1.5rem;
}
.quiz-choices {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}
@media (max-width: 30em) {
  .quiz-choices {
    grid-template-columns: 1fr;
  }
}
.quiz-choice {
  padding: 0.75rem 1rem;
  transition:
    background-color 0.15s ease,
    color 0.15s ease,
    border-color 0.15s ease;
}
.quiz-choice-correct {
  background-color: #1e7e34;
  border-color: #1e7e34;
  color: white;
}
.quiz-choice-wrong {
  background-color: #dc3545;
  border-color: #dc3545;
  color: white;
}
.card-flip-enter-active,
.card-flip-leave-active {
  transition:
    transform 0.25s ease,
    opacity 0.25s ease;
}
.card-flip-enter-from {
  transform: rotateY(90deg);
  opacity: 0;
}
.card-flip-leave-to {
  transform: rotateY(-90deg);
  opacity: 0;
}
.quiz-results {
  max-width: 30rem;
}
</style>
