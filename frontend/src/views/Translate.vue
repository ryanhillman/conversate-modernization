<template>
  <div class="text-center">
    <RequireProfile>
      <div class="card-style">
        <h2>Translate</h2>
      </div>
      <div class="back-card">
        <div class="m-3">
          <label for="selectInputLanguage">Select Input Language</label>
          <br />
          <select
            id="selectInputLanguage"
            v-model="inputLanguage"
            name="selectInputLanguage"
            class="form-select lang-select"
            aria-label="Select input language"
          >
            <option v-for="language in languages" :key="language.code" :value="language.code">
              {{ language.name }}
            </option>
          </select>
        </div>
        <div class="m-3">
          <label for="selectOutputLanguage">Select Output Language</label>
          <br />
          <select
            id="selectOutputLanguage"
            v-model="outputLanguage"
            name="selectOutputLanguage"
            class="form-select lang-select"
            aria-label="Select output language"
          >
            <option v-for="language in languages" :key="language.code" :value="language.code">
              {{ language.name }}
            </option>
          </select>
        </div>
        <p v-if="sameLanguageOnBothSides" class="small m-2">
          Input and output language must be different.
        </p>
        <div>
          <textarea
            class="m-2 translate-textarea"
            aria-label="Text to translate"
            :lang="inputLanguage"
            rows="10"
            maxlength="5000"
            placeholder="Type here to translate…"
            v-model="textToTranslate"
          ></textarea>
          <div class="m-3">
            <button
              v-if="micSupported && !busy"
              type="button"
              class="icon-button"
              :aria-label="recording ? 'Stop recording' : 'Start recording'"
              @click="toggleRecording"
            >
              <Icon
                name="microphone"
                class="icon-3x m-2"
                :class="recording ? 'text-danger' : 'translate-icon'"
              />
            </button>
            <button
              v-if="translatedText && !translatedTextTooLong && !busy"
              type="button"
              class="icon-button"
              aria-label="Listen to translation"
              @click="startTextToSpeech"
            >
              <Icon name="volume-up" class="icon-3x m-2 translate-icon" />
            </button>
            <p v-else-if="translatedTextTooLong" class="text-muted small m-2">
              Translation is too long to read aloud.
            </p>
          </div>
          <textarea
            class="m-2 translate-textarea"
            aria-label="Translation"
            :lang="translatedTextLanguage"
            disabled
            v-model="translatedText"
            rows="10"
          ></textarea>
        </div>
        <br />
        <button
          :disabled="!textToTranslate.trim() || sameLanguageOnBothSides || busy"
          class="btn btn-accent m-3"
          @click="translateEnteredText()"
        >
          Translate
        </button>
      </div>
    </RequireProfile>
  </div>
</template>
<script setup>
import { ref, computed, onBeforeUnmount } from "vue";
import Icon from "../components/Icon.vue";
import RequireProfile from "../components/RequireProfile.vue";
import { translateText } from "../api/translate";
import { synthesizeSpeech } from "../api/tts";
import { transcribeSpeech } from "../api/stt";
import { showToast } from "../stores/toastStore";

const MIC_MIME_TYPE = "audio/webm;codecs=opus";
const MAX_TTS_LENGTH = 5000;
const MAX_RECORDING_MS = 30000;

function blobToBase64(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result.split(",")[1]);
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

const recording = ref(false);
const busy = ref(false);
const textToTranslate = ref("");
const translatedText = ref(null);
// The language translatedText is actually written in, captured at
// translation time — not the live picker, which the user can change
// afterward without re-translating.
const translatedTextLanguage = ref(null);
const inputLanguage = ref("en");
const outputLanguage = ref("it");
const languages = [
  { code: "en", name: "English" },
  { code: "it", name: "Italian" },
];

let mediaRecorder = null;
let audioChunks = [];
let micStream = null;
let recordingTimeout = null;
let leavingPage = false;

const micSupported = computed(
  () =>
    !!(
      navigator.mediaDevices &&
      window.MediaRecorder &&
      MediaRecorder.isTypeSupported(MIC_MIME_TYPE)
    ),
);
const translatedTextTooLong = computed(() => {
  if (!translatedText.value) return false;
  // Google's TTS limit is measured in UTF-8 bytes, not JS string length
  // (UTF-16 code units) — accented characters take more than one byte.
  return new TextEncoder().encode(translatedText.value).length > MAX_TTS_LENGTH;
});
const sameLanguageOnBothSides = computed(() => inputLanguage.value === outputLanguage.value);

onBeforeUnmount(() => {
  // Stopping the tracks below fires the recorder's own "stop" handler,
  // which would otherwise still kick off a paid transcription call for a
  // page the user has already left.
  leavingPage = true;
  clearTimeout(recordingTimeout);
  if (micStream) {
    micStream.getTracks().forEach((track) => track.stop());
  }
});

async function translateEnteredText() {
  busy.value = true;
  try {
    const { translated_text: result } = await translateText(
      textToTranslate.value,
      inputLanguage.value,
      outputLanguage.value,
    );
    translatedText.value = result;
    translatedTextLanguage.value = outputLanguage.value;
  } catch (err) {
    console.error("Translation failed:", err);
    translatedText.value = null;
    translatedTextLanguage.value = null;
    showToast("Could not translate.", "error");
  } finally {
    busy.value = false;
  }
}

async function toggleRecording() {
  if (recording.value) {
    mediaRecorder.stop();
    return;
  }
  let stream;
  try {
    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  } catch (err) {
    console.error("Microphone access denied:", err);
    showToast("Microphone access is required to record.", "error");
    return;
  }
  micStream = stream;
  audioChunks = [];
  mediaRecorder = new MediaRecorder(stream, { mimeType: MIC_MIME_TYPE });
  mediaRecorder.addEventListener("dataavailable", (event) => {
    if (event.data.size > 0) audioChunks.push(event.data);
  });
  mediaRecorder.addEventListener("stop", () => {
    clearTimeout(recordingTimeout);
    micStream.getTracks().forEach((track) => track.stop());
    recording.value = false;
    if (!leavingPage) transcribeRecording();
  });
  mediaRecorder.start();
  recording.value = true;
  recordingTimeout = setTimeout(() => mediaRecorder.stop(), MAX_RECORDING_MS);
}

async function transcribeRecording() {
  busy.value = true;
  try {
    const blob = new Blob(audioChunks, { type: MIC_MIME_TYPE });
    const audio = await blobToBase64(blob);
    const { transcript } = await transcribeSpeech(audio, MIC_MIME_TYPE, inputLanguage.value);
    textToTranslate.value = transcript;
  } catch (err) {
    console.error("Transcription failed:", err);
    const message = err.status === 422 ? "No speech detected." : "Could not transcribe audio.";
    showToast(message, "error");
  } finally {
    busy.value = false;
  }
}

async function startTextToSpeech() {
  busy.value = true;
  try {
    const { audio_content } = await synthesizeSpeech(
      translatedText.value,
      translatedTextLanguage.value,
    );
    await new Audio(`data:audio/mpeg;base64,${audio_content}`).play();
  } catch (err) {
    console.error("Speech synthesis failed:", err);
    showToast("Could not play audio.", "error");
  } finally {
    busy.value = false;
  }
}
</script>
<style scoped>
.translate-textarea {
  width: 100%;
  max-width: 30rem;
  box-sizing: border-box;
  resize: none;
}
/* Real buttons, so the mic and speaker can be reached with Tab and used by
   screen readers, but drawn as just the icon. The browser's focus outline
   is kept so keyboard users can see which one is selected. */
.icon-button {
  background: none;
  border: 0;
  padding: 0;
  color: inherit;
  cursor: pointer;
}
.translate-icon {
  color: var(--brand-navy);
  cursor: pointer;
}
.translate-icon:hover {
  color: var(--brand-navy-dark);
}
.back-card {
  border-radius: var(--radius);
  box-shadow: var(--card-shadow);
  border: var(--card-border);
  padding: 1.5rem;
  margin: 2rem auto;
  max-width: 40rem;
  color: var(--text-color);
  background-color: var(--card-bg);
  font-weight: 400;
}
.lang-select {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  display: inline-block;
  width: auto;
  min-width: 13rem;
  padding: 0.55rem 2.2rem 0.55rem 1rem;
  border: 1px solid var(--bs-secondary);
  border-radius: 8px;
  background-color: #fff;
  color: var(--text-color);
  font-family: "Poppins", sans-serif;
  font-weight: 500;
  cursor: pointer;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 10 6' fill='%2316335c'%3E%3Cpath d='M0 0l5 6 5-6z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.9rem center;
  background-size: 0.7rem;
  transition:
    border-color 0.15s,
    box-shadow 0.15s;
}
.lang-select:hover {
  border-color: var(--brand-accent);
}
.lang-select:focus {
  border-color: var(--brand-navy);
  box-shadow: 0 0 0 3px rgba(224, 168, 46, 0.25);
  outline: none;
}
</style>
