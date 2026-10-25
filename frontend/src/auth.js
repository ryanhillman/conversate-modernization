import { createAuth0 } from "@auth0/auth0-vue";

// Fail fast with a clear message, like the backend's ConfigError, instead of
// letting Log in send the browser to https://undefined/authorize.
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
