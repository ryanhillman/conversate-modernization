import { ref, computed, watch, onBeforeUnmount } from "vue";
import { checkUsername as apiCheckUsername } from "../api/users";
import { usernameError } from "../utils/usernameValidation";

// Shared debounced username-availability check for the create and rename forms.
// Takes the host's `username` ref. `skipAvailabilityCheck` can be overridden
// to suppress the request for values the host already considers available
// (e.g. the user's own current name).
export function useUsernameAvailability(username, { skipAvailabilityCheck = () => false } = {}) {
  // Separate from the host's own "saving" flag for the actual create/rename
  // call: a debounced availability check settling after Save is clicked
  // must not re-enable the button mid-save. True from the keystroke, not just
  // once the request starts, so Save can't submit a taken name during the
  // debounce wait.
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
      // Auth failures, outages, and network errors must not masquerade as
      // "taken" — only an explicit available:false does.
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

  onBeforeUnmount(() => clearTimeout(checkTimer));

  return { checking, takenUsername, validationError };
}
