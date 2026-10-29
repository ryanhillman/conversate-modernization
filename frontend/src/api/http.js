import { auth0 } from "../auth";

// An empty VITE_API_URL means same origin, for a deployment that proxies /api
// to the backend; only an unset one falls back to local dev. A production
// build has to say which, or it would quietly call localhost.
if (import.meta.env.PROD && import.meta.env.VITE_API_URL === undefined) {
  throw new Error(
    "Set VITE_API_URL for production builds: the API's origin, or empty for the same origin.",
  );
}
const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:5000";

// Errors from getAccessTokenSilently() meaning no session can renew, so the
// user has to log in again.
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
      // A dead session must prompt a login, not fall through to 401s.
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
  // 204 is a success with no body (e.g. account deletion); any other success
  // must be JSON, or something is misrouted.
  if (res.status === 204) return undefined;
  const data = await res.json().catch(() => undefined);
  if (!res.ok || data === undefined) {
    const error = new Error((data && data.error) || `Request failed: ${res.status}`);
    error.status = res.status;
    // A machine-readable reason, when the server gives one.
    if (data?.code) error.code = data.code;
    throw error;
  }
  return data;
}
