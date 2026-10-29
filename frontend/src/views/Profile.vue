<template>
  <RequireProfile>
    <h1 class="visually-hidden">Profile</h1>
    <div class="row align-items-center profile-header">
      <div class="col-md-2 mb-3">
        <img
          :src="user.picture"
          alt=""
          referrerpolicy="no-referrer"
          class="rounded-circle img-fluid profile-picture"
        />
      </div>
      <div class="col-md text-center text-md-start">
        <p class="mb-2"><strong>Name:</strong> {{ user.name }}</p>
        <p class="mb-2"><strong>Email:</strong> {{ user.email }}</p>
        <p class="mb-2"><strong>Username:</strong> {{ profile.username }}</p>
        <p class="mb-2">
          <strong>Best quiz score:</strong>
          {{ profile.quiz_best_score ?? "—" }}
        </p>
        <p class="mb-2">
          <strong>Best quiz time:</strong>
          {{ profile.quiz_best_score != null ? formatTime(profile.quiz_best_time_seconds) : "—" }}
        </p>
      </div>
      <div class="col-md text-center text-md-start">
        <AccountActions />
      </div>
    </div>
  </RequireProfile>
</template>

<script setup>
import { useAuth0 } from "@auth0/auth0-vue";
import RequireProfile from "../components/RequireProfile.vue";
import AccountActions from "../components/account/AccountActions.vue";
import { profile } from "../stores/profileStore";
import { formatTime } from "../utils/formatTime";

const { user } = useAuth0();
</script>

<style scoped>
.profile-header {
  text-align: center;
  margin-bottom: 3rem;
}
.profile-header .profile-picture {
  aspect-ratio: 1;
  object-fit: cover;
  box-shadow: 0 0 4px 0 var(--bs-gray-500);
  margin-bottom: 1.5rem;
}
@media (min-width: 768px) {
  .profile-header {
    text-align: left;
  }
  .profile-header .profile-picture {
    margin-bottom: inherit;
  }
}
</style>
