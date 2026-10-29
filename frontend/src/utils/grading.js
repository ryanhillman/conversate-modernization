// Lesson answers are graded ignoring capitalization, extra spaces, and end
// punctuation ("Good evening!"). Accents still count.

export function normalizeAnswer(value) {
  return (value || "")
    .trim()
    .toLowerCase()
    .replace(/[.!?]+$/, "")
    .replace(/\s+/g, " ")
    .trim();
}

export function isAnswerCorrect(value, correctAnswers) {
  const answer = normalizeAnswer(value);
  return answer !== "" && correctAnswers.some((correct) => normalizeAnswer(correct) === answer);
}

// Complete once every question has a correct answer. A lesson with no
// questions is completed with its own button instead.
export function isLessonComplete(questions, answers) {
  return (
    questions.length > 0 &&
    questions.every((question) => isAnswerCorrect(answers[question.id], question.correctAnswers))
  );
}
