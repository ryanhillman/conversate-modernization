const MIN_USERNAME_LENGTH = 3;
const MAX_USERNAME_LENGTH = 100;
const USERNAME_PATTERN = /^[A-Za-z0-9_.-]+$/;

export function usernameError(name) {
  const value = (name || "").trim();
  if (value.length < MIN_USERNAME_LENGTH) {
    return `Username must be at least ${MIN_USERNAME_LENGTH} characters`;
  }
  if (value.length > MAX_USERNAME_LENGTH) {
    return `Username must be at most ${MAX_USERNAME_LENGTH} characters`;
  }
  if (!USERNAME_PATTERN.test(value)) {
    return "Username may only contain letters, numbers, and _ . -";
  }
  return null;
}
