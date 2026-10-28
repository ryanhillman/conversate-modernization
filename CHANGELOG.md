# Changelog

## [Unreleased]

### Added
- Added GitHub Actions CI.
- Added frontend unit and component tests with Vitest.
- Added a Delete account option to the profile page.
- Added an API endpoint reference to the README.
- Added Dependabot to keep backend, frontend, and GitHub Actions dependencies up to date.
- Added accessibility linting and Vue's recommended ESLint rules.
- Added an untimed practice quiz that isn't saved to the leaderboard.
- Added hover effects: a navy underline on nav links, and a gold glow on the home cards, Translate mic and speaker, Log in button, and profile picture.
- Added red shading and an X icon to wrong lesson answers.
- Made animations finish instantly when the system asks for reduced motion.

### Changed
- **Breaking:** The API's user_name field is now username.
- **Breaking:** The migration history is replaced with a single baseline (the user table is now account; databases from 1.x must be recreated).
- Made pages reuse the loaded profile instead of fetching it on every visit.
- Made the profile page read and update the shared profile store directly.
- Read completed lessons from the shared profile store in one place.
- Cached text-to-speech audio, so replaying the same text doesn't call Google again.
- Reused connections to Google's APIs instead of opening a new one for every request.
- Kept idle connections to Google open for 60 seconds instead of 5.
- Shrank the home page images by about 75% by resizing and converting them to WebP.
- Indexed the leaderboard query and fetched only the columns it shows.
- Made lesson completion load and lock the user in one query instead of two.
- Stopped re-reading the user from the database after saving changes.
- Shortened Translate recordings from 60 to 30 seconds, stated the limit, and added each transcript to the text instead of replacing it.
- Extended the speech-to-text timeout from 10 to 40 seconds.
- Colored the checkmarks on Mastery's completed lessons green.
- Restyled completed lessons with a green check on the card's corner and a green title and Toggle button.
- Put each lesson's title and Toggle button on one row.
- Spaced out opened lessons and practice answers.
- Checked lesson answers on Enter or leaving the box, not while typing.
- Stated the quiz's length, time limit, and pause rules before it starts.
- Consistently used color tokens instead of hard-coded colors.
- Moved all global CSS into app.css.
- Styled lesson buttons by class instead of element.
- Fetched Auth0's signing keys with PyJWT's built-in client instead of custom code.
- Switched database queries to SQLAlchemy 2.0's select() style.
- Declared database columns with typed annotations.
- Stored quiz times as timezone-aware UTC.
- Updated README's How to Run: Docker database address, .env.example files, and Google Cloud billing.
- Upgraded Vue Router to 5 and Auth0's Vue SDK to 2.11.
- Upgraded SQLAlchemy to 2.1, Alembic to 1.20, and Gunicorn to 26.2, and switched the Postgres driver to psycopg 3.
- Upgraded the GitHub Actions used in CI.
- Raised the Node requirement to 22.22.2 (or 24.15), which the frontend's tools need.

### Removed
- Removed the old Auth0 wrapper's $auth compatibility layer.
- Removed unused and repeated code.

### Fixed
- Made the "View leaderboard" button on the quiz results screen visible by switching from navy-on-navy to amber.
- Stopped the phone menu showing two active-page markers.
- Ignored .env.local files in Git.
- Showed the home page images in full instead of cropping.
- Lined up the profile page with the other pages.
- Matched the username setup field to the profile page's.
- Stopped gray space showing below the footer on short pages.
- Stopped a gray box showing behind the Translate image.
- Raised text, icon, border, and focus ring contrast to meet WCAG minimums.
- Prevented double-clicking a quiz answer from highlighting the footer logo.
- Made every control usable by keyboard and screen readers, announced results and errors, and marked Italian text for correct pronunciation.
- Made Escape close the profile menu.
- Turned the profile menu and Log out links into buttons; the menu closes when focus leaves.
- Made the Log out menu item's hover highlight visible.
- Made the current page's text on the nav bar navy to match its underline.
- Made the frontend fail with a clear message when its Auth0 settings are missing.
- Reported a taken username, rather than an existing profile, when two people claim the same name at once.
- Kept Save disabled until the username availability check finishes, so a taken name can't be submitted by clicking quickly.
- Stated the text-to-speech length limit in bytes, which is how it's measured, rather than characters.
- Stopped rejecting out-of-order quiz answers as too fast.
- Logged the reason the server rejects a login.
- Retried Auth0's key download after a dropped connection.
- Kept keyboard focus visible and in place.
- Let a quiz result be saved again after a failed submit.
- Showed quiz and recording states with more than color.
- Gave each page its own title, a main landmark, and a skip link.
- Gave every page one h1 and headings that don't skip levels, with a heading per lesson.
- Gave the username and Translate text boxes visible labels.
- Named the conjugation buttons "Play" plus the word.
- Linked the username boxes to their error, and marked them invalid, only while an error shows.
- Hid repeated images from screen readers: the home card images, the footer logo, and the phone menu's profile picture.
- Kept error messages on screen until dismissed.
- Stopped long error messages from running off the left edge on narrow screens.
- Kept error messages from covering the control with keyboard focus, and enlarged their Dismiss button.
- Titled the username setup screen for what it shows.
- Switched to the phone menu when a larger default text size leaves no room for the full nav bar, and let the username fields grow with the text.
- Let the quiz's status row wrap instead of running off narrow screens with wider text spacing.
- Showed a leaderboard load failure on the page instead of an empty leaderboard.
- Stopped a double-clicked microphone from staying on.
- Showed migration command errors instead of exiting silently.
- Made the 30-a-minute limit on Google calls apply per user across translation and speech, not per endpoint and server process.
- Corrected Lesson 2's "ciao ciao" examples, which said hello instead of goodbye.
- Returned a clear error, not a server error, when Google sends speech-to-text an unexpected response.
- Rejected translation requests whose source and target languages match.
- Stopped screen readers reading the check mark before each lesson on Mastery.
- Replaced two quiz words whose answer was the word itself.
- Moved practice instructions below the practice heading.
- Corrected Lesson 7, which called *capire* irregular.
- Told learners to type pronoun answers, not select them.
- Said when a username was taken while saving, instead of a generic error.
- Warned that resetting progress and deleting an account can't be undone.

## [1.0.0] - 2026-10-22

### Added
- Set up Prettier (frontend) and ruff (backend) for consistent formatting and import order.
- Added a fade transition between routes using Vue Router 4’s v-slot form of router-view.
- Added a 404 view for unknown routes.
- Added pytest coverage for authentication, application endpoints, and API integrations.
- Added the option to hear Italian conjugations in lessons.
- Added "✓ Completed" indicators to completed lessons.
- Lesson 8 is now finished with a "Mark lesson complete" button and counts toward mastery.
- Confetti plays after completing a lesson.
- Implemented username checking for parameters and availability while typing.
- Added toast notifications.
- Added a Profile option to the home page.
- Created quiz and leaderboard features that were planned in the original.
- Added an animated Mastery progress bar.
- Added animations for correct lesson answers and card hovering.
- Added .env.example templates for both backend and frontend.
- Added a backend /health endpoint.

### Changed
- Upgraded the frontend to Vue 3 and Vue Router 4.
- Upgraded Node from 10 to 22.
- Converted all components from the Options API to the Composition API (`<script setup>`).
- Replaced Vue CLI/webpack with Vite.
- Migrated ESLint to a flat configuration compatible with Vue 3.
- Upgraded Bootstrap 4 to 5.
- Moved Bootstrap from a CDN to a local dependency.
- Replaced the three Font Awesome packages with one inline SVG icon component containing the app’s three icons.
- Replaced Axios with the native fetch API and a small wrapper for authenticated backend requests.
- Replaced jQuery and Bootstrap's JavaScript with Vue state for the navbar's mobile collapse, profile dropdown, and error banner dismissal.
- Converted authenticated routes from eager loading to lazy-loaded route chunks.
- Upgraded to Python 3.14, Flask 3.1, SQLAlchemy 2.0, Flask-SQLAlchemy 3.1, Flask-Migrate 4.1, Gunicorn 26.0, Alembic 1.18, and all other backend dependencies.
- Replaced Flask-Script and manage.py with Flask's built-in CLI for database migrations.
- Replaced the custom Auth0 wrapper with the official Vue SDK.
- Changed account identity from email addresses to immutable Auth0 sub identifiers.
- Replaced user-specific account endpoints with /api/me.
- Rewrote `Lesson.vue` as a single data-driven template, moving lesson content into `data/lessons.js` (~1,380 → ~600 lines combined, measured before formatting with Prettier).
- Made lesson answer checking ignore capitalization.
- Replaced the score counter with lesson completion tracking on the Mastery page.
- Initially setting a username now redirects user to the home page.
- Improved design with new fonts and a cohesive color palette.
- Centered the navigation bar.
- Replaced the unofficial translate feature with the official Google Cloud Translation API.
- Replaced the browser Speech API with Google Cloud Text-to-Speech and Speech-to-Text.
- Replaced the original's Alembic history with a new baseline migration.
- Standardized API error responses as JSON instead of HTML.
- Replaced full-table scans with indexed queries.
- Added settings to the profile page and removed settings from drop down menu.
- Replaced full account deletion with a progress reset that keeps your account and username.
- Replaced internal navigation links with Vue Router's router-link.
- Centralized user API calls in a shared module.
- Centralized profile loading and account setup in a shared component.
- Extracted shared styles from component style blocks.
- Renamed functions, identifiers, and methods for clearer intent and maintainability.
- Improved error handling for profile and lesson requests.
- Consolidated the original's .gitignore rules into a single root .gitignore.
- Replaced the original's frontend Dockerfile with a containerized backend.

### Removed
- Removed Babel, Sass, and related build dependencies, which Vite doesn't need.
- Removed the backend Pipfile and left requirements.txt as the single dependency source.
- Removed unused games and question components, routes, imports, the flash card table, and the questions API endpoints.
- Removed outdated project references.

### Fixed
- Lesson answers are now keyed per question.
- Made answer boxes start neutral, only turning red once something wrong is typed.
- Typing your own current username no longer reads as "taken."
- Prevented the username setup form from flashing on authenticated pages.
- Fixed application tabs to highlight when active.
- Added descriptive alt text to images.
- Applied spelling and grammar corrections to English and Italian content.
- Derived Mastery lesson counts directly from lesson data.
- Standardized username handling across account creation, renaming, and availability checks.
- Enforced account and username uniqueness at the database level, returning 409 conflict when concurrent requests collide.
- Made HTML element IDs unique across lesson questions.

### Security
- Set DEBUG to default to False.
- Secured the API with Auth0 access-token authentication and JWT validation (automatically picking up Auth0's rotated signing keys), so accounts can no longer be read, renamed, deleted, or have their score changed by anyone who knows the email.
- Removed the user-list endpoint, which returned every user's email to unauthenticated requests.
- Required authentication for the username-availability check.
- Added a global route guard that requires authentication by default.
- Added server-side validation for API request bodies.
- Capped the maximum request body size.
- Rate-limited the paid translation and speech endpoints per user.

[Unreleased]: https://github.com/ryanhillman/conversate-modernization/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/ryanhillman/conversate-modernization/releases/tag/v1.0.0
