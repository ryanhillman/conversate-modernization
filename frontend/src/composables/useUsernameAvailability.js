import { ref, computed, watch, onBeforeUnmount } from "vue";
import { checkUsername as apiCheckUsername } from "../api/users";
import { announce } from "../stores/announceStore";
import { usernameError } from "../utils/usernameValidation";

// Debounced username checks for the create and rename forms.
// skipAvailabilityCheck skips the request for names the host knows are fine,
// e.g. the user's own.
export function useUsernameAvailability(username, { skipAvailabilityCheck = () => false } = {}) {
  // True from the keystroke until the check returns, so Save can't submit a
  // taken name meanwhile.
  const checking = ref(false);
  const takenUsername = ref(false);
  let checkTimer = null;
  let checkSeq = 0;

  const validationError = computed(() => usernameError(username.value));

  async function checkUsername(candidate, seq) {
    try {
      const data = await apiCheckUsername(candidate);
      // Ignore a response a newer keystroke has already superseded.
      if (seq === checkSeq) takenUsername.value = !data.available;
    } catch {
      if (seq !== checkSeq) return;
      // Only an explicit available: false means taken; errors don't.
      takenUsername.value = false;
    } finally {
      // A superseded check must not clear the flag a newer one still holds.
      if (seq === checkSeq) checking.value = false;
    }
  }

  watch(username, (val) => {
    clearTimeout(checkTimer);
    takenUsername.value = false;
    const seq = ++checkSeq;
    const candidate = val.trim();
    if (validationError.value || skipAvailabilityCheck(candidate)) {
      checking.value = false;
      return;
    }
    checking.value = true;
    checkTimer = setTimeout(() => checkUsername(candidate, seq), 400);
  });

  // The error shown under the field; nothing until something is typed.
  const errorMessage = computed(() => {
    if (username.value && validationError.value) return validationError.value;
    return takenUsername.value ? "That username is taken" : "";
  });
  // Errors appear as you type, so announce them to screen readers.
  watch(errorMessage, (message) => {
    if (message) announce(message);
  });

  // Someone can take the name between the check and saving. Marks it taken
  // and returns true when that's why saving failed.
  function takenOnSave(err) {
    if (err?.code !== "username_taken") return false;
    takenUsername.value = true;
    return true;
  }

  onBeforeUnmount(() => clearTimeout(checkTimer));

  return { checking, takenUsername, validationError, errorMessage, takenOnSave };
}
