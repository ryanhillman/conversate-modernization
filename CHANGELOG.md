# Changelog

## [2.0.0] - 2026-10-29

### Breaking
- The API's user_name field is now username, and the profile response no longer includes id.
- The migration history is replaced with a single baseline; the user table is now account, so databases from 1.x must be recreated.
- The frontend's tools need Node 22.22.2+, 24.15+, or 26+.

### Added
- An untimed practice quiz that isn't saved to the leaderboard.
- A Delete account option on the profile page; it and Reset progress warn that they can't be undone.
- Frontend unit and component tests with Vitest, GitHub Actions CI, Dependabot, and accessibility linting with Vue's recommended ESLint rules.
- An API endpoint reference in the README, and a username_taken code on the API's taken-username errors.
- A robots.txt.
- Hover effects: a navy underline on nav links, and a gold glow on the home cards, the Translate mic and speaker, Log in, and the profile picture; a light sweeps across the home page's welcome once per browser session.
- Reduced-motion support: animations finish instantly when the system asks for less motion.

### Changed
- Translate: recordings are 30 seconds, down from 60, and say so while recording; each transcript is added to the text instead of replacing it; the prompts sit inside the boxes, the mic and Translate button between them, and Listen below the translation.
- Lessons: answers are checked on Enter or on leaving the box, ignoring end punctuation and extra spaces, and wrong ones get red shading and an X; each lesson has an Open lesson or Close lesson button beside its title; completed lessons get a green check, title, and button.
- Quiz: the start screen says the quiz is timed; a pause holds the clock for as long as it lasts; Practice shows just the question count above the card.
- Username: setting one keeps you on the page you were on; the prompt sits inside the box, and Save username is now Save.
- Pages reuse the loaded profile instead of fetching it on every visit, text-to-speech audio is cached, and connections to Google's APIs are reused.
- Speech-to-text waits up to 20 seconds for Google, instead of 8.
- The home page images are about 75% smaller, resized and converted to WebP.
- The backend runs as one Gunicorn worker with 16 threads and a matching database connection pool, so rate limits are counted in one place and no request waits for a connection.
- Quiz times are stored as timezone-aware UTC, and the leaderboard query is indexed.
- Updated dependencies: Vue Router 5, Auth0's Vue SDK 2.11, SQLAlchemy 2.1, Alembic 1.20, Gunicorn 26.2, and the Postgres driver psycopg 3.
- Two API errors reworded: Profile not found and Profile already exists.
- The README's How to Run covers the Docker database address, the .env.example files, Google Cloud billing, and restricting the API key.
- Visual polish across every page: site colors on buttons and checkmarks, matching button sizes, consistent spacing, an evenly spaced and centered nav bar, and the profile page lined up with the rest.
- Internal: color tokens, one global stylesheet, SQLAlchemy 2.0 query style, typed model columns, and PyJWT's built-in JWKS client.

### Removed
- The old Auth0 wrapper's $auth compatibility layer.

### Fixed
- Accessibility, structure: every page has one h1, headings that don't skip levels (with a heading per lesson), a main landmark, a skip link, and its own title.
- Accessibility, keyboard and focus: every control is reachable by keyboard, including the translation; focus stays visible (also in Windows High Contrast mode) and moves to whatever replaces a control that disappears; Escape closes the profile menu, which also closes when focus leaves.
- Accessibility, screen readers: results, errors, and status changes are announced; Italian is marked with lang="it"; controls are named (Play plus the word, Open or Close lesson plus its title, Account menu, the quiz timer); a completed lesson's heading says so; quiz and recording states are shown with more than color; repeated images and decorative check marks are hidden.
- Accessibility, contrast: text, icons, borders, and focus rings meet WCAG AA.
- Accessibility, larger text: the nav collapses to the phone menu when the full one won't fit, fields grow with the text, and nothing is clipped or scrolls sideways at 320px with wider text spacing.
- Error messages stay until dismissed, with a larger Dismiss button, don't cover the focused control, and fit narrow screens; a leaderboard that fails to load says so instead of showing empty.
- Quiz: out-of-order answers were rejected as too fast; an answer given as the quiz paused, or a click while the card flipped, ended it or answered the next question unseen; an answer whose reply was lost ended it early when sent again; nothing right counted as a best and reached the leaderboard as 0; a failed submit couldn't be retried; a double-click could highlight the footer logo; two words were their own answer.
- Translate: words after a pause in a recording were dropped; a double-clicked microphone stayed on; same-language requests are rejected; an unexpected Google response, or the rate limit, gets a clear message; a missing microphone is explained; the text-to-speech limit is stated in bytes, as it's measured.
- Lessons: Lesson 2's "ciao ciao" said hello instead of goodbye; *capire* moved to Lesson 6 as a regular *-ire* pattern; pronoun answers are typed, not selected; practice instructions follow their heading; titles, prompts, and translations are consistent in quotes, punctuation, and capitalization.
- Username: Enter saves on both forms; a taken name is reported as such, even when two people claim it at once; Save stays disabled until the availability check finishes; password managers no longer offer the sign-in email; the error is linked to the box only while it shows.
- Pages stayed blank when the profile loaded during the page fade-in, did nothing after a new version was deployed until a refresh, and opened where the last page was scrolled to instead of at the top.
- Several controls were hard to see: the quiz results' View leaderboard button (navy on navy), the Log out item's hover, and the Log in button when focused.
- Layout: the home page images show in full, no gray strip shows below the footer or behind the Translate image, the profile menu stays inside 1200px screens, and the phone menu no longer shows two active-page markers.
- The 30-a-minute limit on Google calls applies per user across translation and speech, not per endpoint and server process.
- The backend returns a 400, not a server error, for deeply nested JSON; migration command errors are shown instead of exiting silently; all local .env files are ignored by Git; a local virtual environment is kept out of the Docker image.
- The frontend fails with a clear message when its Auth0 settings are missing; the server logs why it rejects a login and retries Auth0's key download after a dropped connection.

### Security
- The backend's code is read-only to the user it runs as.
- Access tokens missing an expiry or issue time are rejected.
- A signing key Auth0 revokes is trusted for at most an hour, down from ten hours.

## [1.0.0] - 2026-10-22

### Breaking
- Accounts are identified by their Auth0 ID instead of email, and the per-user account endpoints are replaced by /api/me.
- The original's Alembic history is replaced with a new baseline migration.
- The frontend builds with Vite on Node 22, up from Vue CLI on Node 10.

### Added
- A quiz and a leaderboard, which the original had planned.
- In lessons: Italian conjugations can be played aloud, correct answers animate, confetti plays on completion, and Lesson 8 is finished with a Mark lesson complete button that counts toward mastery.
- An animated Mastery progress bar, with completed lessons marked "✓ Completed".
- Username checks while typing, for format and availability.
- Toast notifications, a 404 page, and a Profile card on the home page.
- A backend /health endpoint, and .env.example templates for both apps.
- Backend tests with pytest covering authentication, the endpoints, and the Google integrations; Prettier and ruff for formatting.

### Changed
- Translation uses the Google Cloud Translation API, and speech uses Google Cloud Text-to-Speech and Speech-to-Text, replacing an unofficial translator and the browser's Speech API.
- Account settings moved from the drop-down menu to the profile page, and full account deletion became a progress reset that keeps your username.
- Mastery tracks completed lessons instead of a score counter, and lesson answers ignore capitalization.
- Setting a username for the first time goes to the home page.
- A new design: new fonts, a cohesive color palette, a centered nav bar, and a fade between pages.
- API errors are JSON instead of HTML, and the main queries use indexes instead of full-table scans.
- Updated dependencies: Vue 3, Vue Router 4, Bootstrap 5 (installed locally, not from a CDN), the official Auth0 Vue SDK, Python 3.14, Flask 3.1, SQLAlchemy 2.0, Flask-SQLAlchemy 3.1, Flask-Migrate 4.1, Alembic 1.18, and Gunicorn 26.0; migrations run through Flask's CLI instead of Flask-Script.
- The backend is containerized instead of the frontend.
- Internal: Composition API with `<script setup>`, lazy-loaded pages, fetch instead of Axios, Vue state instead of jQuery and Bootstrap's JavaScript, one inline SVG icon component instead of Font Awesome, lesson content as data in one template, shared modules for the user API and profile loading, shared styles, clearer names, better error handling for profile and lesson requests, a flat ESLint config, and one root .gitignore.

### Removed
- Babel, Sass, the backend Pipfile, and other build dependencies Vite doesn't need.
- The unused games and question components, routes, the flash card table, and the questions API endpoints.

### Fixed
- Lesson answers are keyed per question, answer boxes start neutral and only turn red once something wrong is typed, and element IDs are unique across questions.
- Typing your own current username no longer reads as taken, the setup form no longer flashes on signed-in pages, and username handling is the same across creation, renaming, and the availability check.
- Account and username uniqueness is enforced by the database, with a 409 when concurrent requests collide.
- The nav bar highlights the current page, images have descriptive alt text, Mastery's lesson counts come from the lesson data, and spelling and grammar are corrected in the English and Italian content.

### Security
- The API requires Auth0 access tokens, validated as JWTs with Auth0's rotated signing keys picked up automatically; before, anyone who knew an email could read, rename, or delete the account or change its score.
- The user-list endpoint, which gave every user's email to unauthenticated requests, is removed, and the username-availability check requires authentication.
- Every route requires sign-in by default.
- Request bodies are validated server-side and capped in size, and the paid translation and speech endpoints are rate-limited per user.
- DEBUG defaults to off.

[2.0.0]: https://github.com/ryanhillman/conversate-modernization/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/ryanhillman/conversate-modernization/releases/tag/v1.0.0
