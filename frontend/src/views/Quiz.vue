<template>
  <RequireProfile>
    <div class="text-center">
      <!-- The title shows until a quiz starts; after that, only screen readers
           get it, named for the mode being played. -->
      <div v-if="phase === 'ready'" class="card-style">
        <h1 class="h2">Timed Quiz</h1>
      </div>
      <h1 v-else class="visually-hidden">{{ practice ? "Practice" : "Timed Quiz" }}</h1>

      <div v-if="phase === 'ready'" class="card-style quiz-narrow">
        <div class="quiz-buttons">
          <button ref="startButton" class="btn btn-accent" @click="start(false)">Start</button>
          <button class="btn btn-practice" @click="start(true)">Practice</button>
        </div>
      </div>

      <div v-else-if="phase === 'loading'" class="loading-state">
        <p>Loading…</p>
      </div>

      <div v-else-if="phase === 'active' || phase === 'paused'" class="quiz-card-wrap">
        <!-- Practice has only the question count, so it sits in the middle. -->
        <div class="quiz-meta" :class="{ 'justify-content-center': practice }">
          <span>Question {{ currentIndex + 1 }} / {{ questions.length }}</span>
          <template v-if="!practice">
            <span class="quiz-timer"
              ><span class="visually-hidden">Time left: </span>{{ formattedRemaining }}</span
            >
            <span class="quiz-pauses">Pauses left: {{ pausesRemaining }}</span>
            <button
              v-if="phase === 'active' && pausesRemaining > 0"
              class="btn btn-sm btn-outline-primary"
              :class="{ disabled: advancing }"
              :aria-disabled="advancing"
              @click="pause"
            >
              Pause
            </button>
          </template>
        </div>

        <div v-if="phase === 'paused'" class="quiz-card quiz-paused">
          <p>Paused</p>
          <button ref="resumeButton" class="btn btn-accent" @click="resume">Resume</button>
        </div>
        <transition v-else name="card-flip" mode="out-in" @after-enter="cardShown">
          <div :key="currentIndex" class="quiz-card">
            <h2 ref="questionWord" class="h3 quiz-word" lang="it" tabindex="-1">
              {{ currentQuestion.it }}
            </h2>
            <div class="quiz-choices">
              <button
                v-for="choice in currentQuestion.choices"
                :key="choice"
                class="btn btn-outline-primary quiz-choice"
                :class="[choiceClass(choice), { disabled: advancing }]"
                :aria-disabled="advancing"
                @click="selectAnswer(choice)"
              >
                <span v-if="choiceClass(choice)" aria-hidden="true">{{
                  feedback === "correct" ? "✓" : "✗"
                }}</span>
                {{ choice }}
              </button>
            </div>
          </div>
        </transition>
      </div>

      <div
        v-else-if="phase === 'results'"
        ref="resultsCard"
        class="card-style quiz-narrow"
        tabindex="-1"
      >
        <h2 v-if="result.is_new_best" class="h3">New best!</h2>
        <p v-if="result.practice">Practice result, not saved to the leaderboard.</p>
        <p>Score: {{ result.score }} / {{ questions.length }}</p>
        <p>Time: {{ formatTime(result.time_seconds) }}</p>
        <div class="quiz-buttons quiz-end-buttons">
          <button class="btn btn-accent" @click="start(practice)">Play again</button>
          <router-link to="/leaderboard" class="btn btn-accent">View leaderboard</router-link>
        </div>
      </div>

      <div v-else-if="phase === 'error'" class="card-style">
        <p>Could not load the quiz.</p>
        <button ref="retryButton" class="btn btn-accent" @click="start(practice)">Try again</button>
      </div>

      <div v-else-if="phase === 'saveError'" class="card-style">
        <p>Could not save your result.</p>
        <button ref="retryButton" class="btn btn-accent" @click="finish">Try again</button>
      </div>
    </div>
  </RequireProfile>
</template>

<script setup>
import { ref, computed, watch, onBeforeUnmount } from "vue";
import RequireProfile from "../components/RequireProfile.vue";
import { startQuiz, answerQuiz, pauseQuiz, resumeQuiz, submitQuiz } from "../api/quiz";
import { profile, setProfile } from "../stores/profileStore";
import { announce } from "../stores/announceStore";
import { showToast } from "../stores/toastStore";
import { formatTime } from "../utils/formatTime";

const FEEDBACK_DISPLAY_MS = 500;

const phase = ref("ready");
// Untimed, and not saved to the leaderboard.
const practice = ref(false);
const questions = ref([]);
const currentIndex = ref(0);
const result = ref(null);
const advancing = ref(false);
const selectedChoice = ref(null);
const feedback = ref(null);
const remainingSeconds = ref(0);
const pausesRemaining = ref(0);
let tickTimer = null;
// When the clock was last synced with the server, and its reading then.
let displayStart = 0;
let secondsRemainingAtStart = 0;

const currentQuestion = computed(() => questions.value[currentIndex.value]);
const formattedRemaining = computed(() => formatTime(remainingSeconds.value));

onBeforeUnmount(() => clearInterval(tickTimer));

const startButton = ref(null);
const questionWord = ref(null);
const resumeButton = ref(null);
const resultsCard = ref(null);
const retryButton = ref(null);

// Each screen replaces the one that had focus, so move focus onto the new one.
const FOCUS_TARGETS = {
  ready: startButton,
  active: questionWord,
  paused: resumeButton,
  results: resultsCard,
  error: retryButton,
  saveError: retryButton,
};
watch(phase, (newPhase) => FOCUS_TARGETS[newPhase]?.value?.focus(), { flush: "post" });

// A new question's card has flipped in: it can take answers now, and focus.
// Until then a click would land on the old card, still flipping out, and be
// sent as an answer to the new question.
function cardShown() {
  advancing.value = false;
  questionWord.value?.focus();
}

function choiceClass(choice) {
  if (choice !== selectedChoice.value || !feedback.value) return "";
  return feedback.value === "correct" ? "quiz-choice-correct" : "quiz-choice-wrong";
}

function resetDisplayClock(secondsRemaining) {
  displayStart = Date.now();
  secondsRemainingAtStart = secondsRemaining;
  remainingSeconds.value = secondsRemaining;
}

function tick() {
  const elapsed = Math.floor((Date.now() - displayStart) / 1000);
  remainingSeconds.value = Math.max(0, secondsRemainingAtStart - elapsed);
  if (remainingSeconds.value === 0) {
    finish();
  }
}

async function start(isPractice) {
  clearInterval(tickTimer);
  practice.value = isPractice;
  phase.value = "loading";
  try {
    const data = await startQuiz(isPractice);
    questions.value = data.questions;
    currentIndex.value = 0;
    advancing.value = false;
    selectedChoice.value = null;
    feedback.value = null;
    pausesRemaining.value = data.pauses_remaining;
    phase.value = "active";
    if (!isPractice) {
      resetDisplayClock(data.seconds_remaining);
      tickTimer = setInterval(tick, 1000);
    }
  } catch (err) {
    console.error("Failed to start quiz:", err);
    phase.value = "error";
    // Focus goes to Try again, so the message itself has to be announced.
    announce("Could not load the quiz.");
  }
}

async function pause() {
  if (phase.value !== "active" || advancing.value) return;
  // An answer sent meanwhile would reach the server paused and be refused,
  // which ends the quiz.
  advancing.value = true;
  try {
    const data = await pauseQuiz();
    clearInterval(tickTimer);
    phase.value = "paused";
    remainingSeconds.value = data.seconds_remaining;
    pausesRemaining.value = data.pauses_remaining;
  } catch (err) {
    console.error("Failed to pause quiz:", err);
    showToast("Could not pause the quiz.", "error");
  } finally {
    advancing.value = false;
  }
}

async function resume() {
  if (phase.value !== "paused") return;
  try {
    const data = await resumeQuiz();
    // Paused just as time ran out: there's nothing left to resume.
    if (data.seconds_remaining <= 0) return finish();
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
    announce(correct ? "Correct" : "Incorrect");
  } catch (err) {
    console.error("Failed to submit answer:", err);
    selectedChoice.value = null;
    if (err.code === "out_of_sync") {
      // The answer's first try was graded but its reply was lost: move on.
      showToast("Your earlier answer was already counted.", "success");
      nextQuestion();
    } else if (err.status === 409) {
      // Time ran out or the quiz is gone: finish with what's been graded.
      finish();
    } else {
      // Other failures may be temporary, so let the user retry.
      showToast("Could not submit your answer. Try again.", "error");
      advancing.value = false;
    }
    return;
  }
  setTimeout(() => {
    selectedChoice.value = null;
    feedback.value = null;
    nextQuestion();
  }, FEEDBACK_DISPLAY_MS);
}

function nextQuestion() {
  if (currentIndex.value < questions.value.length - 1) {
    currentIndex.value += 1;
  } else {
    finish();
  }
}

async function finish() {
  if (!["active", "paused", "saveError"].includes(phase.value)) return;
  clearInterval(tickTimer);
  phase.value = "loading";
  try {
    result.value = await submitQuiz();
    // Submit returns only this attempt, so update the stored best directly.
    if (result.value.is_new_best && profile.value) {
      setProfile({
        ...profile.value,
        quiz_best_score: result.value.score,
        quiz_best_time_seconds: result.value.time_seconds,
      });
    }
    phase.value = "results";
  } catch (err) {
    console.error("Failed to submit quiz:", err);
    // 409: no quiz in progress, e.g. an earlier submit saved but its response
    // was lost, so retrying can't help. Other failures may be temporary.
    if (err.status === 409) {
      showToast("This quiz is no longer in progress.", "error");
      phase.value = "ready";
    } else {
      phase.value = "saveError";
      announce("Could not save your result.");
    }
  }
}
</script>

<style scoped>
.quiz-card-wrap {
  max-width: 40rem;
  margin: 0 auto;
  /* A double-click that misses the flipping card would select the nearest text. */
  user-select: none;
}
.quiz-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 1rem;
}
/* Solid white, second to the gold Start on the navy card. */
.btn-practice {
  --bs-btn-color: var(--brand-navy);
  --bs-btn-bg: var(--card-bg);
  --bs-btn-border-color: var(--card-bg);
  --bs-btn-hover-color: var(--brand-navy);
  --bs-btn-hover-bg: var(--border-subtle);
  --bs-btn-hover-border-color: var(--border-subtle);
  --bs-btn-active-color: var(--brand-navy);
  --bs-btn-active-bg: var(--border-subtle);
  --bs-btn-active-border-color: var(--border-subtle);
}
/* The site's navy, not Bootstrap's blue, for Pause and the answers. */
.btn-outline-primary {
  --bs-btn-color: var(--brand-navy);
  --bs-btn-border-color: var(--brand-navy);
  --bs-btn-hover-color: var(--text-on-dark);
  --bs-btn-hover-bg: var(--brand-navy);
  --bs-btn-hover-border-color: var(--brand-navy);
  --bs-btn-active-color: var(--text-on-dark);
  --bs-btn-active-bg: var(--brand-navy-dark);
  --bs-btn-active-border-color: var(--brand-navy-dark);
  --bs-btn-disabled-color: var(--brand-navy);
  --bs-btn-disabled-border-color: var(--brand-navy);
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
}
/* Bootstrap's .disabled lets clicks fall through to the page, where a
   double-click's second click selected text. Busy choices keep the click and
   ignore it (selectAnswer returns early), and don't look pressed. */
.quiz-choice.disabled {
  pointer-events: auto;
  cursor: default;
  --bs-btn-active-color: var(--bs-btn-disabled-color);
  --bs-btn-active-bg: var(--bs-btn-disabled-bg);
  --bs-btn-active-border-color: var(--bs-btn-disabled-border-color);
}
/* The other choices dim while the answer is checked; the feedback stays at
   full contrast. */
.quiz-choice-correct,
.quiz-choice-wrong {
  opacity: 1;
}
/* Feedback only shows on a busy choice, so it sets the disabled colors. */
.quiz-choice-correct {
  --bs-btn-disabled-color: var(--text-on-dark);
  --bs-btn-disabled-bg: var(--success);
  --bs-btn-disabled-border-color: var(--success);
}
.quiz-choice-wrong {
  --bs-btn-disabled-color: var(--text-on-dark);
  --bs-btn-disabled-bg: var(--bs-danger);
  --bs-btn-disabled-border-color: var(--bs-danger);
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
/* The start and results cards. */
.quiz-narrow {
  max-width: 30rem;
}
/* Side by side and the same width, stacking when they don't fit. */
.quiz-buttons {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1rem;
}
.quiz-buttons .btn {
  min-width: min(var(--quiz-button-width, 8rem), 100%);
}
/* Room for View leaderboard. */
.quiz-end-buttons {
  --quiz-button-width: 11rem;
}
</style>
