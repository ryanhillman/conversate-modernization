## Changelog

**Framework & build (Vue 3 + Vite)**
- Upgraded the frontend to Vue 3 and Vue Router 4.
- Replaced Vue CLI/webpack with Vite.
- Removed unused Babel, Sass, and related build dependencies.
- Migrated ESLint to a flat configuration compatible with Vue 3.
- Upgraded Bootstrap 4 to 5.
- Moved Bootstrap from a CDN to a local dependency.
- Removed jQuery and Bootstrap JavaScript by replacing the navbar's mobile collapse and profile dropdown with Vue state, then added click-outside handling for the profile dropdown.
- Replaced the three Font Awesome packages with one inline SVG icon component containing the app’s three icons.
- Replaced Axios with the native fetch API and a small wrapper for authenticated backend requests.
- Added a controlled RichText renderer for the italic and bold formatting used by lesson content.
- Added a fade transition between routes using Vue Router 4’s v-slot form of router-view.
- Converted authenticated routes from eager loading to lazy-loaded route chunks.
- Added a 404 view for unknown routes.

**Backend runtime & dependencies**
- Upgraded to Python 3.14, Flask 3.1, SQLAlchemy 2.0, Flask-SQLAlchemy 3.1, Flask-Migrate 4.1, Gunicorn 26.0, and Alembic 1.18.
- Replaced Flask-Script and manage.py with Flask's built-in CLI for database migrations.
- Removed the backend Pipfile and left requirements.txt as the single dependency source.
- Set DEBUG to default to False.

**Testing**
- Added pytest coverage for authentication, application endpoints, and API integrations.
- Configured the pytest suite to run against both SQLite and PostgreSQL.

**Authentication**
- Replaced the custom Auth0 wrapper with the official Vue SDK.
- Secured the API with Auth0 access-token authentication, JWT validation, and automatic signing-key rotation.
- Changed account identity from email addresses to immutable Auth0 sub identifiers.
- Replaced user-specific account endpoints with /api/me.
- Required authentication for the username-availability check.
- Added a global route guard that requires authentication by default.

**Lessons & UX**
- Rewrote the Lessons view as a single data-driven template (~1,380 → ~600 lines).
- Lesson answers are now keyed per question.
- Made lesson answer checking ignore capitalization.
- Added the option to hear Italian conjugations in lessons.
- Added lesson completion tracking to the Mastery page.
- Added "✓ Completed" indicators to completed lessons.
- Lesson 8 is now finished with a "Mark lesson complete" button and counts toward mastery.
- Confetti plays after completing a lesson.
- Made answer boxes start neutral, only turning red once something wrong is typed.
- Typing your own current username no longer reads as "taken." 
- Initially setting a username now redirects user to the home page.
- Implemented username checking for parameters and availability while typing.
- Prevented the username setup form from flashing on authenticated pages.
- Added toast notifications.
- Let Vue manage error banner dismissal instead of Bootstrap JavaScript.
- Added a Profile option to the home page.

**Quiz & Leaderboard**
- Created quiz and leaderboard features that were planned in the original.

**UI & design**
- Improved design with new fonts and a cohesive color palette.
- Added/improved animations for the mastery bar, correct-answers, and buttons.
- Centered the navigation bar.
- Fixed application tabs to highlight when active.
- Added descriptive alt text to images.
- Applied spelling and grammar corrections to English and Italian content.

**Backend & API**
- Replaced the unofficial translate feature with the official Google Cloud Translation API.
- Replaced the browser Speech API with Google Cloud Text-to-Speech and Speech-to-Text.
- Centralized Google Cloud API requests and error handling in a shared backend module.
- Added dedicated API endpoints for lesson completion and progress reset.
- Derived Mastery lesson counts directly from lesson data.
- Standardized username handling across account creation, renaming, and availability checks.
- Enforced account and username uniqueness at the database level, returning 409 conflict when concurrent requests collide.
- Consolidated the Alembic migration history into a single baseline.
- Added incremental migrations for the quiz schema.
- Standardized API error responses as JSON instead of HTML.
- Validated required configuration at application startup to fail if required settings are missing.
- Replaced full-table scans with indexed queries and database-side sorting.
- Added timeouts for outbound requests.
- Added server-side validation for API request bodies.

**Cleanup**
- Removed unused games components, routes, and imports.
- Added settings to the profile page and removed settings from drop down menu.
- Replaced internal navigation links with Vue Router's router-link.
- Centralized user API calls in a shared module.
- Centralized profile loading and account setup in a shared component.
- Extracted shared styles from component style blocks.
- Removed unused user-list and account deletion API endpoints.
- Renamed functions, identifiers, and methods for clearer intent and maintainability.
- Removed outdated project references.
- Made HTML element IDs unique across lesson questions.
- Improved error handling for shared profile and lesson requests.

**Set up**
- Consolidated the original's .gitignore rules into a single root .gitignore.
- Added .env.example templates for both backend and frontend.
- Replaced the original's frontend Dockerfile with a containerized backend.
- Added a backend /health endpoint.