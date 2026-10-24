import { auth0 } from "../auth";

// An empty VITE_API_URL means "same origin" (production, where the reverse
// proxy routes /api/* to the backend); only a genuinely unset value falls
// back to local dev.
const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:5000";

// login_required/consent_required come from getAccessTokenSilently() finding
// no usable session at all. missing_refresh_token/invalid_grant come from it
// finding a session whose refresh token can't renew the access token (never
// issued, or itself expired) — same dead end, just a different error code.
const RELOGIN_ERRORS = [
  "login_required",
  "consent_required",
  "missing_refresh_token",
  "invalid_grant",
];

// Fetch wrapper for the backend API: attaches the Auth0 access token, sends
// JSON, and throws an Error with a `status` property on non-2xx responses.
export async function api(path, { method = "GET", body, timeoutMs = 10000 } = {}) {
  const headers = {};
  if (auth0.isAuthenticated.value) {
    try {
      const token = await auth0.getAccessTokenSilently();
      headers.Authorization = `Bearer ${token}`;
    } catch (e) {
      // A dead or revoked session must prompt re-login, never fall through and
      // hit the API unauthenticated (which just surfaces as 401 error toasts).
      if (RELOGIN_ERRORS.includes(e.error)) {
        auth0.loginWithRedirect();
      }
      throw e;
    }
  }
  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
  }
  const res = await fetch(BASE_URL + path, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
    signal: AbortSignal.timeout(timeoutMs),
  });
  // 204 No Content is a success with no body by design (e.g. deleting the
  // account); any other success must be JSON, or something is misrouted.
  if (res.status === 204) return undefined;
  const data = await res.json().catch(() => undefined);
  if (!res.ok || data === undefined) {
    const error = new Error((data && data.error) || `Request failed: ${res.status}`);
    error.status = res.status;
    throw error;
  }
  return data;
}
