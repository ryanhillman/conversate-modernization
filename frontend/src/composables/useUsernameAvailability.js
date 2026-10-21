import { ref, computed, watch, onBeforeUnmount } from "vue";
import { checkUsername as apiCheckUsername } from "../api/users";
import { usernameError } from "../utils/usernameValidation";

// Shared debounced username-availability check for the create and rename forms.
// Takes the host's `username` ref. `skipAvailabilityCheck` can be overridden
// to suppress the request for values the host already considers available
// (e.g. the user's own current name).
export function useUsernameAvailability(username, { skipAvailabilityCheck = () => false } = {}) {
  const processing = ref(false);
  const takenUsername = ref(false);
  let checkTimer = null;
  let checkSeq = 0;

  const validationError = computed(() => usernameError(username.value));

  function checkUsername(candidate, seq) {
    processing.value = true;
    apiCheckUsername(candidate)
      .then(() => {
        // Ignore a response a newer keystroke has already superseded.
        if (seq === checkSeq) takenUsername.value = false;
      })
      .catch((err) => {
        if (seq !== checkSeq) return;
        // Only a 409 means the name is taken; auth failures, outages, and
        // network errors must not masquerade as "taken".
        takenUsername.value = err.status === 409;
      })
      .finally(() => {
        processing.value = false;
      });
  }

  watch(username, (val) => {
    clearTimeout(checkTimer);
    takenUsername.value = false;
    const seq = ++checkSeq;
    const candidate = val.trim();
    if (validationError.value || skipAvailabilityCheck(candidate)) return;
    checkTimer = setTimeout(() => checkUsername(candidate, seq), 400);
  });

  onBeforeUnmount(() => clearTimeout(checkTimer));

  return { processing, takenUsername, validationError };
}
