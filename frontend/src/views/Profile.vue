<template>
  <div class="container">
    <RequireProfile v-slot="{ user, setUser }">
      <div class="row align-items-center profile-header">
        <div class="col-md-2 mb-3">
          <img
            :src="authUser.picture"
            alt="User's profile picture"
            class="rounded-circle img-fluid profile-picture"
          />
        </div>
        <div class="col-md text-center text-md-start">
          <p class="mb-2"><strong>Name:</strong> {{ authUser.name }}</p>
          <p class="mb-2"><strong>Email:</strong> {{ authUser.email }}</p>
          <p class="mb-2"><strong>Username:</strong> {{ user.username }}</p>
          <p class="mb-2">
            <strong>Best quiz score:</strong>
            {{ user.quiz_best_score ?? "—" }}
          </p>
          <p class="mb-2">
            <strong>Time:</strong>
            {{ user.quiz_best_score != null ? formatTime(user.quiz_best_time_seconds) : "—" }}
          </p>
        </div>
        <div class="col-md text-center text-md-start">
          <AccountActions :current-username="user.username" @updated="setUser" />
        </div>
      </div>
    </RequireProfile>
  </div>
</template>

<script setup>
import { useAuth0 } from "@auth0/auth0-vue";
import RequireProfile from "../components/RequireProfile.vue";
import AccountActions from "../components/username/AccountActions.vue";
import { formatTime } from "../utils/formatTime";

// Named apart from the slot's user, which is the Conversate profile.
const { user: authUser } = useAuth0();
</script>
