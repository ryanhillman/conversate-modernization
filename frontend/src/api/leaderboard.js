import { api } from "./http";

export function getLeaderboard() {
  return api("/api/leaderboard");
}
