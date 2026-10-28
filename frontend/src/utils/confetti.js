const COLORS = [
  "var(--brand-navy)",
  "var(--brand-accent)",
  "var(--success)",
  "var(--confetti-blue)",
  "var(--bs-danger)",
];

export function generateConfetti(count = 60) {
  return Array.from({ length: count }, (_, i) => ({
    left: `${Math.random() * 100}%`,
    background: COLORS[i % COLORS.length],
    animationDelay: `${Math.random() * 0.5}s`,
    animationDuration: `${2 + Math.random() * 1.5}s`,
    transform: `rotate(${Math.random() * 360}deg)`,
  }));
}
