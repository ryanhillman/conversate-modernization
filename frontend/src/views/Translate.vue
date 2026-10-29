<template>
  <div class="text-center">
    <RequireProfile>
      <div class="card-style">
        <h1 class="h2">Translate</h1>
      </div>
      <div class="back-card">
        <div class="m-3">
          <label class="d-block" for="selectInputLanguage">Input language</label>
          <select id="selectInputLanguage" v-model="inputLanguage" class="form-select lang-select">
            <option v-for="language in languages" :key="language.code" :value="language.code">
              {{ language.name }}
            </option>
          </select>
        </div>
        <div class="m-3">
          <label class="d-block" for="selectOutputLanguage">Output language</label>
          <select
            id="selectOutputLanguage"
            v-model="outputLanguage"
            class="form-select lang-select"
          >
            <option v-for="language in languages" :key="language.code" :value="language.code">
              {{ language.name }}
            </option>
          </select>
        </div>
        <p v-if="sameLanguageOnBothSides" class="form-error small m-2">
          Input and output language must be different.
        </p>
        <!-- Each box's prompt is a placeholder, gone once the box has text.
             That's fine for WCAG because the page makes each box's purpose
             clear: the one box to type in sits under Input language, and
             the read-only box follows the Translate button. Screen readers
             get the same words from the hidden labels. -->
        <div class="translate-field">
          <label for="textToTranslate" class="visually-hidden">Enter here to translate…</label>
          <textarea
            id="textToTranslate"
            v-model="textToTranslate"
            class="form-control translate-textarea"
            :lang="inputLanguage"
            :maxlength="MAX_TEXT_LENGTH"
            placeholder="Enter here to translate…"
          ></textarea>
        </div>
        <!-- Busy buttons use aria-disabled, not disabled: a disabled button loses keyboard focus. -->
        <div class="m-3">
          <button
            v-if="micSupported"
            type="button"
            class="icon-button"
            :aria-disabled="busy || startingMic"
            :aria-label="recording ? 'Stop recording' : 'Start recording'"
            aria-describedby="mic-hint"
            @click="toggleRecording"
          >
            <Icon
              name="microphone"
              class="icon-3x m-2"
              :class="recording ? 'text-danger' : 'translate-icon'"
            />
          </button>
          <p v-if="recording" class="small m-2">
            <strong>Recording, up to {{ MAX_RECORDING_SECONDS }} seconds.</strong> Select the
            microphone again to stop.
          </p>
          <!-- Screen readers hear the limit on the mic button, before recording:
               announced during it, speech on speakers would be recorded too. -->
          <p v-if="micSupported" id="mic-hint" class="visually-hidden">
            Recordings stop after {{ MAX_RECORDING_SECONDS }} seconds and are added to the text.
          </p>
          <p v-else class="text-muted small m-2">Voice input isn't available in this browser.</p>
        </div>
        <button
          :disabled="!textToTranslate.trim() || sameLanguageOnBothSides"
          :aria-disabled="busy"
          class="btn btn-accent mb-3"
          :class="{ disabled: busy }"
          @click="translateEnteredText()"
        >
          Translate
        </button>
        <div class="translate-field">
          <label for="translation" class="visually-hidden">Translation</label>
          <textarea
            id="translation"
            :value="translatedText"
            class="form-control translate-textarea"
            :lang="translatedTextLanguage"
            readonly
            placeholder="Translation"
          ></textarea>
        </div>
        <div v-if="translatedText" class="m-3">
          <button
            v-if="!translatedTextTooLong"
            type="button"
            class="icon-button"
            :aria-disabled="busy"
            aria-label="Listen to translation"
            @click="startTextToSpeech"
          >
            <Icon name="volume-up" class="icon-3x m-2 translate-icon" />
          </button>
          <p v-else class="text-muted small m-2">Translation is too long to read aloud.</p>
        </div>
      </div>
    </RequireProfile>
  </div>
</template>
<script setup>
import { ref, computed, watch, onBeforeUnmount } from "vue";
import Icon from "../components/Icon.vue";
import RequireProfile from "../components/RequireProfile.vue";
import { translateText } from "../api/translate";
import { synthesizeSpeech } from "../api/tts";
import { transcribeSpeech } from "../api/stt";
import { announce } from "../stores/announceStore";
import { showToast } from "../stores/toastStore";
import { rateLimitMessage } from "../utils/rateLimitMessage";

const MIC_MIME_TYPE = "audio/webm;codecs=opus";
const MAX_TTS_LENGTH = 5000;
const MAX_RECORDING_SECONDS = 30;
const MAX_TEXT_LENGTH = 5000;

function blobToBase64(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result.split(",")[1]);
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

const recording = ref(false);
const startingMic = ref(false);
const busy = ref(false);
const textToTranslate = ref("");
const translatedText = ref(null);
// The language translatedText is in, captured when translated; the picker may
// have changed since.
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

const micSupported = !!(
  navigator.mediaDevices &&
  window.MediaRecorder &&
  MediaRecorder.isTypeSupported(MIC_MIME_TYPE)
);
const translatedTextTooLong = computed(() => {
  if (!translatedText.value) return false;
  // Google's limit is in UTF-8 bytes, and accented letters take more than one.
  return new TextEncoder().encode(translatedText.value).length > MAX_TTS_LENGTH;
});
const sameLanguageOnBothSides = computed(() => inputLanguage.value === outputLanguage.value);

// These messages appear without moving focus, so tell screen readers.
watch(sameLanguageOnBothSides, (same) => {
  if (same) announce("Input and output language must be different.");
});
watch(translatedTextTooLong, (tooLong) => {
  if (tooLong) announce("Translation is too long to read aloud.");
});

onBeforeUnmount(() => {
  // Stopping the tracks fires the recorder's stop handler; leavingPage keeps
  // it from starting a paid transcription.
  leavingPage = true;
  clearTimeout(recordingTimeout);
  if (micStream) {
    micStream.getTracks().forEach((track) => track.stop());
  }
});

async function translateEnteredText() {
  if (busy.value) return;
  busy.value = true;
  try {
    const { translated_text: result } = await translateText(
      textToTranslate.value,
      inputLanguage.value,
      outputLanguage.value,
    );
    translatedText.value = result;
    translatedTextLanguage.value = outputLanguage.value;
    // The result appears while focus stays on the button, so say it arrived.
    announce("Translation ready.");
  } catch (err) {
    console.error("Translation failed:", err);
    translatedText.value = null;
    translatedTextLanguage.value = null;
    showToast(rateLimitMessage(err, "Could not translate."), "error");
  } finally {
    busy.value = false;
  }
}

async function toggleRecording() {
  if (busy.value) return;
  if (recording.value) {
    mediaRecorder.stop();
    return;
  }
  // A second click while the microphone starts would open a second stream
  // that nothing stops.
  if (startingMic.value) return;
  startingMic.value = true;
  let stream;
  try {
    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  } catch (err) {
    console.error("Microphone access denied:", err);
    showToast("Microphone access is required to record.", "error");
    return;
  } finally {
    startingMic.value = false;
  }
  // The page was left while the permission prompt was open.
  if (leavingPage) {
    stream.getTracks().forEach((track) => track.stop());
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
    stream.getTracks().forEach((track) => track.stop());
    recording.value = false;
    if (!leavingPage) transcribeRecording();
  });
  mediaRecorder.start();
  recording.value = true;
  recordingTimeout = setTimeout(() => mediaRecorder.stop(), MAX_RECORDING_SECONDS * 1000);
}

async function transcribeRecording() {
  busy.value = true;
  try {
    const blob = new Blob(audioChunks, { type: MIC_MIME_TYPE });
    const audio = await blobToBase64(blob);
    const { transcript } = await transcribeSpeech(audio, MIC_MIME_TYPE, inputLanguage.value);
    // Added to what's there, so a long message can be spoken in parts. Capped
    // at the box's maxlength, as typing is.
    textToTranslate.value = [textToTranslate.value.trim(), transcript]
      .filter(Boolean)
      .join(" ")
      .slice(0, MAX_TEXT_LENGTH);
    announce("Transcript added.");
  } catch (err) {
    console.error("Transcription failed:", err);
    const message = err.status === 422 ? "No speech detected." : "Could not transcribe audio.";
    showToast(rateLimitMessage(err, message), "error");
  } finally {
    busy.value = false;
  }
}

async function startTextToSpeech() {
  if (busy.value) return;
  busy.value = true;
  try {
    const { audio_content } = await synthesizeSpeech(
      translatedText.value,
      translatedTextLanguage.value,
    );
    await new Audio(`data:audio/mpeg;base64,${audio_content}`).play();
  } catch (err) {
    console.error("Speech synthesis failed:", err);
    showToast(rateLimitMessage(err, "Could not play audio."), "error");
  } finally {
    busy.value = false;
  }
}
</script>
<style scoped>
.translate-field {
  max-width: 30rem;
  margin: 0.5rem auto;
  text-align: start;
}
.translate-textarea {
  height: 15rem;
  resize: none;
}
/* Read-only rather than disabled, so the translation can be focused and
   selected; shaded so it doesn't look editable. */
.translate-textarea[readonly] {
  background-color: var(--bs-secondary-bg);
}
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
.icon-button .translate-icon {
  transition: filter 0.15s ease;
}
.icon-button:hover .translate-icon,
.icon-button:focus-visible .translate-icon {
  filter: drop-shadow(0 0 6px color-mix(in srgb, var(--brand-accent) 80%, transparent));
}
.icon-button[aria-disabled="true"] {
  opacity: 0.5;
}
.icon-button[aria-disabled="true"],
.icon-button[aria-disabled="true"] .translate-icon {
  cursor: default;
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
  /* Never wider than the card on phones with larger text. */
  min-width: min(13rem, 100%);
  padding: 0.55rem 2.2rem 0.55rem 1rem;
  border: 1px solid var(--bs-secondary);
  border-radius: 8px;
  color: var(--text-color);
  font-family: var(--font-heading);
  font-weight: 500;
  cursor: pointer;
  /* Room for the focus ring below the label. */
  margin-top: 0.4rem;
}
.lang-select:hover {
  border-color: var(--brand-navy);
}
</style>
