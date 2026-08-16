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
        <p>Time: {{ formattedTime(result.time_seconds) }}</p>
        <button class="btn btn-accent m-2" @click="start">Play again</button>
        <router-link to="/leaderboard" class="btn btn-primary m-2">
          View leaderboard
        </router-link>
      </div>

      <div v-else-if="phase === 'error'" class="card-style">
        <p>Could not load the quiz.</p>
        <button class="btn btn-accent" @click="start">Try again</button>
      </div>
    </div>
  </RequireProfile>
</template>

<script>
import RequireProfile from "../components/RequireProfile.vue";
import { startQuiz, answerQuiz, pauseQuiz, resumeQuiz, submitQuiz } from "../api/quiz";
import { showToast } from "../stores/toastStore";
import { formatTime } from "../utils/formatTime";

const FEEDBACK_DISPLAY_MS = 500;

export default {
  name: "Quiz",
  components: {
    RequireProfile,
  },
  data() {
    return {
      phase: "ready",
      questions: [],
      currentIndex: 0,
      result: null,
      advancing: false,
      selectedChoice: null,
      feedback: null,
      displayStart: 0,
      secondsRemainingAtStart: 0,
      remainingSeconds: 0,
      pausesRemaining: 0,
      tickTimer: null,
    };
  },
  computed: {
    currentQuestion() {
      return this.questions[this.currentIndex];
    },
    formattedRemaining() {
      return this.formattedTime(this.remainingSeconds);
    },
  },
  beforeUnmount() {
    clearInterval(this.tickTimer);
  },
  methods: {
    formattedTime: formatTime,
    choiceClass(choice) {
      if (choice !== this.selectedChoice || !this.feedback) return "";
      return this.feedback === "correct" ? "quiz-choice-correct" : "quiz-choice-wrong";
    },
    resetDisplayClock(secondsRemaining) {
      this.displayStart = Date.now();
      this.secondsRemainingAtStart = secondsRemaining;
      this.remainingSeconds = secondsRemaining;
    },
    async start() {
      clearInterval(this.tickTimer);
      this.phase = "loading";
      try {
        const data = await startQuiz();
        this.resetDisplayClock(data.seconds_remaining);
        this.questions = data.questions;
        this.currentIndex = 0;
        this.advancing = false;
        this.selectedChoice = null;
        this.feedback = null;
        this.pausesRemaining = data.pauses_remaining;
        this.phase = "active";
        this.tickTimer = setInterval(this.tick, 1000);
      } catch (err) {
        console.error("Failed to start quiz:", err);
        this.phase = "error";
      }
    },
    tick() {
      const elapsed = Math.floor((Date.now() - this.displayStart) / 1000);
      this.remainingSeconds = Math.max(0, this.secondsRemainingAtStart - elapsed);
      if (this.remainingSeconds === 0) {
        this.finish();
      }
    },
    async pause() {
      if (this.phase !== "active") return;
      try {
        const data = await pauseQuiz();
        clearInterval(this.tickTimer);
        this.phase = "paused";
        this.remainingSeconds = data.seconds_remaining;
        this.pausesRemaining = data.pauses_remaining;
      } catch (err) {
        console.error("Failed to pause quiz:", err);
        showToast("Could not pause the quiz.", "error");
      }
    },
    async resume() {
      if (this.phase !== "paused") return;
      try {
        const data = await resumeQuiz();
        this.resetDisplayClock(data.seconds_remaining);
        this.pausesRemaining = data.pauses_remaining;
        this.phase = "active";
        this.tickTimer = setInterval(this.tick, 1000);
      } catch (err) {
        console.error("Failed to resume quiz:", err);
        showToast("Could not resume the quiz.", "error");
      }
    },
    async selectAnswer(choice) {
      if (this.advancing) return;
      this.advancing = true;
      this.selectedChoice = choice;
      try {
        const { correct } = await answerQuiz(this.currentIndex, choice);
        this.feedback = correct ? "correct" : "wrong";
      } catch (err) {
        console.error("Failed to submit answer:", err);
        // Most likely cause: time ran out server-side between clicking and
        // this request landing. Finalize with whatever's been graded so far
        // instead of leaving the user stuck on a dead question.
        this.finish();
        return;
      }
      setTimeout(() => {
        this.selectedChoice = null;
        this.feedback = null;
        if (this.currentIndex < this.questions.length - 1) {
          this.currentIndex += 1;
          this.advancing = false;
        } else {
          this.finish();
        }
      }, FEEDBACK_DISPLAY_MS);
    },
    async finish() {
      if (this.phase !== "active" && this.phase !== "paused") return;
      clearInterval(this.tickTimer);
      this.phase = "loading";
      try {
        this.result = await submitQuiz();
        this.phase = "results";
      } catch (err) {
        console.error("Failed to submit quiz:", err);
        showToast("Could not submit your quiz result.", "error");
        this.phase = "error";
      }
    },
  },
};
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
  transition: background-color 0.15s ease, color 0.15s ease, border-color 0.15s ease;
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
  transition: transform 0.25s ease, opacity 0.25s ease;
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
