import { createAuth0 } from "@auth0/auth0-vue";

// Fail fast with a clear message instead of Log in going to
// https://undefined/authorize.
const REQUIRED_ENV = ["VITE_AUTH0_DOMAIN", "VITE_AUTH0_CLIENT_ID", "VITE_AUTH0_AUDIENCE"];
const missing = REQUIRED_ENV.filter((name) => !import.meta.env[name]);
if (missing.length) {
  throw new Error(
    `Missing ${missing.join(", ")}. Copy frontend/.env.example to frontend/.env and fill in your Auth0 values.`,
  );
}

export const auth0 = createAuth0({
  domain: import.meta.env.VITE_AUTH0_DOMAIN,
  clientId: import.meta.env.VITE_AUTH0_CLIENT_ID,
  authorizationParams: {
    redirect_uri: window.location.origin,
    audience: import.meta.env.VITE_AUTH0_AUDIENCE,
  },
  cacheLocation: "localstorage",
  useRefreshTokens: true,
});

// Logout returns with a full page load, which resets the profile store.
// Clearing it first would flash the username setup form.
export function logout() {
  auth0.logout({ logoutParams: { returnTo: window.location.origin } });
}
