const COLORS = ["#16335c", "#E0A82E", "#1e7e34", "#2c6df8", "#dc3545"];

export function generateConfetti(count = 60) {
  return Array.from({ length: count }, (_, i) => ({
    left: Math.random() * 100 + "%",
    background: COLORS[i % COLORS.length],
    animationDelay: Math.random() * 0.5 + "s",
    animationDuration: 2 + Math.random() * 1.5 + "s",
    transform: "rotate(" + Math.random() * 360 + "deg)",
  }));
}
