# Changelog

## [Unreleased]

### Added
- Added GitHub Actions CI.

### Changed
- Made pages reuse the loaded profile instead of fetching it on every visit.
- Cached text-to-speech audio, so replaying the same text doesn't call Google again.
- Reused connections to Google's APIs instead of opening a new one for every request.
- Shrank the home page images by about 75% by resizing and converting them to WebP.
- Added a database index for the leaderboard query and fetched only the columns it shows.
- Made lesson completion load and lock the user in one query instead of two.

### Fixed
- Made the "View leaderboard" button on the quiz results screen visible by switching from navy-on-navy to amber.

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
- Let Vue manage error banner dismissal instead of Bootstrap JavaScript.
- Improved design with new fonts and a cohesive color palette.
- Centered the navigation bar.
- Replaced the unofficial translate feature with the official Google Cloud Translation API.
- Replaced the browser Speech API with Google Cloud Text-to-Speech and Speech-to-Text.
- Consolidated the Alembic migration history into a single baseline.
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
- Removed jQuery and Bootstrap JavaScript by replacing the navbar's mobile collapse and profile dropdown with Vue state.
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
