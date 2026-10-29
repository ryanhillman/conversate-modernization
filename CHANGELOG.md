# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0] - 2026-10-29

This release makes every page accessible to WCAG 2.2 AA and adds a practice quiz. The API's user field and the database schema change. Please see the Breaking entries before upgrading.

### Security
- The backend's code is read-only to the user it runs as.
- Access tokens missing an expiry or issue time are rejected.
- A signing key Auth0 revokes is trusted for at most an hour, down from ten hours.

### Removed
- **Breaking:** The unused id from the profile API response.
- The old Auth0 wrapper's $auth compatibility layer.

### Changed
- **Breaking:** The API's user_name field is now username.
- **Breaking:** The migration history is replaced with a single baseline, and the user table is now account, so databases from 1.x must be recreated.
- **Breaking:** The frontend's tools need Node 24 (24.15 or newer); 22.22.2+ and 26+ also work.
- **Breaking:** The quiz actions after start send the attempt_id that start now returns.
- Pages reuse the loaded profile instead of fetching it on every visit.
- Text-to-speech audio is cached, and connections to Google's APIs are reused.
- The home page images are about 75% smaller, resized and converted to WebP.
- The backend runs as one Gunicorn worker with 16 threads, so rate limits are counted in one place, with a database connection for each thread.
- Quiz times are stored as timezone-aware UTC, and the leaderboard query uses an index.
- Two API errors reworded: Profile not found and Profile already exists.
- The README's How to Run covers the Docker database address, the .env.example files, and restricting the Google API key.
- Visual polish across every page: site colors on buttons and checkmarks, matching button sizes, consistent spacing, an evenly spaced and centered nav bar, and the profile page lined up with the rest.

#### Translate
- Recordings stop at 30 seconds, down from 60, and the limit is shown while recording.
- Each transcript is added to the text instead of replacing it.
- The prompts sit inside the boxes; the mic and the Translate button sit between them, and Listen below the translation.

#### Lessons
- Answers are checked on Enter or on leaving the box, not while typing, and ignore end punctuation and extra spaces.
- Wrong answers get red shading and an X.
- Each lesson has an Open lesson or Close lesson button beside its title.
- Completed lessons get a green check, title, and button.

#### Quiz
- The start screen says the quiz is timed.
- A pause holds the clock for as long as it lasts.
- Practice shows just the question count above the card.

#### Username
- Setting one keeps you on the page you were on.
- The prompt sits inside the box, and Save username is now Save.

### Fixed
- Error messages stay until dismissed, have a larger Dismiss button, don't cover the focused control, and fit narrow screens.
- A leaderboard that fails to load says so instead of showing empty.
- Pages stayed blank when the profile loaded during the page fade-in.
- Pages did nothing after a new version was deployed until a refresh.
- Pages opened where the last page was scrolled to instead of at the top.
- Several controls were hard to see: the quiz results' View leaderboard button (navy on navy), the Log out item's hover, and the Log in button when focused.
- Layout: the home page images show in full, no gray strip shows below the footer or behind the Translate image, the profile menu stays inside 1200px screens, and the phone menu no longer shows two active-page markers.
- The 30-a-minute limit on Google calls applies per user across translation and speech, not per endpoint and server process.
- The backend returns a 400, not a server error, for deeply nested JSON.
- Migration command errors are shown instead of exiting silently.
- Flask no longer prints a python-dotenv tip on every command.
- All local .env files are ignored by Git and kept out of the Docker image, as is a local virtual environment.
- The frontend fails with a clear message when its Auth0 settings are missing, or when a production build doesn't say where the API is instead of quietly calling localhost.
- The server logs why it rejects a login, and retries Auth0's key download after a dropped connection.

#### Accessibility
- Every page has one h1, with headings that don't skip levels and a heading per lesson.
- Every page has a main landmark, a skip link, and its own title.
- Every control is reachable by keyboard, including the translation.
- Focus stays visible, also in Windows High Contrast mode, and moves to whatever replaces a control that disappears.
- Escape closes the profile menu, which also closes when focus leaves it.
- Results, errors, and status changes are announced to screen readers.
- Italian is marked as Italian, so screen readers pronounce it correctly.
- Controls are named for screen readers: Play plus the word, Open or Close lesson plus its title, Account menu, and the quiz timer.
- A completed lesson's heading says so.
- Quiz and recording states are shown with more than color.
- Repeated images and decorative check marks are hidden from screen readers.
- Text, icons, borders, and focus rings meet WCAG AA contrast.
- The nav collapses to the phone menu when a larger default text size leaves no room for the full one.
- Fields grow with the text, and nothing is clipped or scrolls sideways at 320px with wider text spacing.

#### Quiz
- Out-of-order answers were rejected as too fast.
- An answer given as the quiz paused ended it.
- A click while the card flipped answered the next question unseen and could highlight the footer logo.
- An answer whose reply was lost ended the quiz early when sent again.
- A quiz started in another tab or browser left the first tab answering into it and submitting it early; the first tab now stops with a message.
- A quiz with nothing right counted as a best and reached the leaderboard as 0.
- A failed submit couldn't be retried.
- Two words were their own answer.

#### Translate
- Words after a pause in a recording were dropped.
- Longer recordings timed out before Google answered; the server now waits up to 20 seconds, not 8.
- A double-clicked microphone stayed on.
- Requests with the same source and target language are rejected.
- An unexpected Google response, or the rate limit, gets a clear message.
- A browser without voice input, or a missing microphone, gets its own message.
- The text-to-speech limit is stated in bytes, as it's measured.

#### Lessons
- Lesson 2's "ciao ciao" examples said hello instead of goodbye.
- *capire* moved to Lesson 6 as a regular *-ire* pattern; Lesson 7 had called it irregular.
- Pronoun answers are typed, not selected.
- Practice instructions follow their heading.
- Titles, prompts, and translations are consistent in quotes, punctuation, and capitalization.

#### Username
- Enter saves on both forms.
- A taken name is reported as taken, even when two people claim it at once.
- Save stays disabled until the availability check finishes.
- Password managers no longer offer the sign-in email.
- The error is linked to the box only while it shows.

### Added
- An untimed practice quiz, not saved to the leaderboard.
- A Delete account option on the profile page. It and Reset progress warn that they can't be undone.
- Frontend unit and component tests with Vitest.
- GitHub Actions CI, Dependabot, and accessibility linting with Vue's recommended ESLint rules.
- An API endpoint reference in the README.
- A username_taken code on the API's taken-username errors, so clients can tell that case apart.
- A robots.txt.
- Hover effects: a navy underline on nav links, and a gold glow on the home cards, the Translate mic and speaker, Log in, and the profile picture.
- A light sweep across the home page's welcome, once per browser session.
- Reduced-motion support: animations finish instantly when the system asks for less motion.

## [1.0.0] - 2026-10-22

This version is the first stage of modernization. It was upgraded to current frameworks/tools, the API was secured, and a quiz/leaderboard were added.

### Security
- The API requires Auth0 access tokens, validated as JWTs with Auth0's rotated signing keys picked up automatically. Before, anyone who knew an email could read, rename, or delete the account or change its score.
- The user-list endpoint, which gave every user's email to unauthenticated requests, is removed.
- The username-availability check requires authentication.
- Every route requires sign-in by default.
- Request bodies are validated server-side and capped in size.
- The paid translation and speech endpoints are rate-limited per user.
- DEBUG defaults to off.

### Removed
- Babel, Sass, the backend Pipfile, and other build dependencies Vite doesn't need.
- The unused games and question components, routes, the flash card table, and the questions API endpoints.

### Changed
- **Breaking:** Accounts are identified by their Auth0 ID instead of email, and the per-user account endpoints are replaced by /api/me.
- **Breaking:** The original's Alembic history is replaced with a new baseline migration.
- **Breaking:** The frontend builds with Vite on Node 22, up from Vue CLI on Node 10, and the backend runs on Python 3.14.
- Translation uses the Google Cloud Translation API, replacing an unofficial translator.
- Speech uses Google Cloud Text-to-Speech and Speech-to-Text, replacing the browser's Speech API.
- Account settings moved from the drop-down menu to the profile page.
- Full account deletion became a progress reset that keeps your username.
- Mastery tracks completed lessons instead of a score counter.
- Lesson answers ignore capitalization.
- Setting a username for the first time goes to the home page.
- A new design: new fonts, a cohesive color palette, a centered nav bar, and a fade between pages.
- API errors are JSON instead of HTML.
- The main queries use indexes instead of full-table scans.
- The frontend runs on Vue 3, Vue Router 4, and Bootstrap 5 (installed locally, not from a CDN), with the official Auth0 Vue SDK; the backend on Flask 3.1 and SQLAlchemy 2.0, with migrations through Flask's CLI instead of Flask-Script.
- The backend is containerized instead of the frontend.

### Fixed
- Account and username uniqueness is enforced by the database, with a 409 when concurrent requests collide.
- The nav bar highlights the current page.
- Images have descriptive alt text.
- Mastery's lesson counts come from the lesson data.
- Spelling and grammar are corrected in the English and Italian content.

#### Lessons
- Answers are keyed per question.
- Answer boxes start neutral and only turn red once something wrong is typed.
- Element IDs are unique across questions.

#### Username
- Typing your own current username no longer reads as taken.
- The setup form no longer flashes on signed-in pages.
- Handling is the same across creation, renaming, and the availability check.

### Added
- A quiz and a leaderboard, which the original had planned.
- An animated Mastery progress bar, with completed lessons marked "✓ Completed".
- Username checks while typing, for format and availability.
- Toast notifications.
- A 404 page.
- A Profile card on the home page.
- A backend /health endpoint.
- .env.example templates for both apps.
- Backend tests with pytest, covering authentication, the endpoints, and the Google integrations.
- Prettier and ruff for formatting.

#### Lessons
- Italian conjugations can be played aloud.
- Correct answers animate, and confetti plays on completing a lesson.
- Lesson 8 is finished, with a Mark lesson complete button that counts toward mastery.

[Unreleased]: https://github.com/ryanhillman/conversate-modernization/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/ryanhillman/conversate-modernization/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/ryanhillman/conversate-modernization/releases/tag/v1.0.0
