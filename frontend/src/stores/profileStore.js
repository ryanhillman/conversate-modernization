import { computed, ref } from "vue";
import { getMe } from "../api/users";

// The signed-in user's profile, loaded once and shared by every view so that
// moving between pages doesn't re-fetch it. Views that change the profile
// (rename, lesson completion, reset, quiz submit) update it here instead of
// triggering another GET /api/me.
export const profile = ref(null);

export const completedLessonIds = computed(() => profile.value?.lessons_completed ?? []);

let pending = null;

export function loadProfile() {
  if (profile.value) return Promise.resolve(profile.value);
  // Several views can mount at once; share one in-flight request.
  if (!pending) {
    pending = getMe()
      .then((data) => {
        profile.value = data;
        return data;
      })
      .finally(() => {
        pending = null;
      });
  }
  return pending;
}

export function setProfile(data) {
  profile.value = data;
}
