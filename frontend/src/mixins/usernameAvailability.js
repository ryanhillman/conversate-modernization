import { checkUsername as apiCheckUsername } from "../api/users";
import { usernameError } from "../utils/usernameValidation";

// Shared debounced username-availability check for the create and rename forms.
// Expects the host component to define a `username` data property. A component
// can override `skipAvailabilityCheck` to suppress the request for values it
// already considers available (e.g. the user's own current name).
export default {
  data() {
    return {
      processing: false,
      takenUsername: false,
      checkTimer: null,
      checkSeq: 0,
    };
  },
  computed: {
    validationError() {
      return usernameError(this.username);
    },
  },
  watch: {
    username(val) {
      clearTimeout(this.checkTimer);
      this.takenUsername = false;
      const seq = ++this.checkSeq;
      const candidate = val.trim();
      if (this.validationError || this.skipAvailabilityCheck(candidate)) return;
      this.checkTimer = setTimeout(() => this.checkUsername(candidate, seq), 400);
    },
  },
  beforeUnmount() {
    clearTimeout(this.checkTimer);
  },
  methods: {
    skipAvailabilityCheck() {
      return false;
    },
    checkUsername(candidate, seq) {
      this.processing = true;
      apiCheckUsername(candidate)
        .then(() => {
          // Ignore a response a newer keystroke has already superseded.
          if (seq === this.checkSeq) this.takenUsername = false;
        })
        .catch((err) => {
          if (seq !== this.checkSeq) return;
          // Only a 409 means the name is taken; auth failures, outages, and
          // network errors must not masquerade as "taken".
          this.takenUsername = err.status === 409;
        })
        .finally(() => {
          this.processing = false;
        });
    },
  },
};
