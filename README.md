# Conversate - Modernization 2026

<p align="center">
  <img src="https://img.shields.io/badge/Security-Auth0-EB5424" />
  <img src="https://img.shields.io/badge/Backend-Flask-000000?logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/Frontend-Vue.js-42B883?logo=vue.js&logoColor=white" />
</p>

Conversate is a full-stack web application for learning Italian. 

[Visit original version of Conversate here.](https://github.com/ryanhillman/conversate-original)

Thank you to everyone involved.

---

## [Demo (v1.0.0)](https://youtu.be/GpFT1M0YnfY)

---

## Screenshot

![Conversate Screenshot](./docs/screenshot.png)

---

## Features

Secure sign-in with Google or email through Auth0.

Interactive grammar lessons and progress tracking.

Translation tool with text-to-speech and speech-to-text options.

Vocabulary quiz with user scores and times ranked on a leaderboard.

---

## Tech Stack

**Backend**
- Python 3.14
- Flask 3.1
- SQLAlchemy 2.1
- Flask-Migrate 4.1 + Alembic 1.20
- Flask-SQLAlchemy 3.1
- Flask-Limiter 4.1
- httpx 0.28
- PostgreSQL 18
- Gunicorn 26.2
- Docker

**Frontend**
- Vue.js 3.5
- Vite 8.3
- Vue Router 5.4
- Bootstrap 5.3
- CSS

**Authentication**
- Auth0
- PyJWT 2.15

**Google Cloud**
- Cloud Translation API
- Text-to-Speech API
- Speech-to-Text API

---

## How to Run

Requires Python 3.14, Node 22.13+, Docker, Auth0, and Google Cloud.

### Auth0

Create a Single Page Application and an API:

- **SPA:** add `http://localhost:3000` to Allowed Callback URLs, Allowed Logout URLs, and Allowed Web Origins. Turn on **Refresh Token Rotation**, and the **Refresh Token** grant type (Advanced Settings → Grant Types).
- **API:** set an identifier, e.g. `https://conversate-api`; it's the audience for both apps. Turn on **Allow Offline Access**, so expired sessions renew silently.

### Google Cloud

In a project with billing enabled (required even within the free tiers), enable the Translation, Text-to-Speech, and Speech-to-Text APIs, and create an API key (APIs & Services → Credentials).

### Environment

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

Fill in the Auth0 domain and audience (both files), the SPA client ID (frontend), and the Google API key (backend). The default `DATABASE_URL` matches the Postgres container below.

### Run

```bash
docker run -d --name conversate-postgres -p 5432:5432 -e POSTGRES_USER=conversate -e POSTGRES_PASSWORD=conversate -e POSTGRES_DB=conversate postgres:18

cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
flask --app run.py db upgrade
python run.py  # http://localhost:5000
```

In a second terminal:

```bash
cd frontend
npm install
npm run dev  # http://localhost:3000
```

On macOS, if port 5000 is taken, turn off AirPlay Receiver (System Settings → General → AirDrop & Handoff).

#### Backend in Docker (optional)

```bash
docker build -t conversate-backend backend
docker run -p 5000:5000 --env-file backend/.env \
  -e DATABASE_URL=postgresql://conversate:conversate@host.docker.internal:5432/conversate \
  --add-host=host.docker.internal:host-gateway \
  conversate-backend
```

Inside the container, `127.0.0.1` is the container itself, so it reaches Postgres through `host.docker.internal`; `--add-host` makes that name work on Linux too. The container doesn't run migrations; run `flask --app run.py db upgrade` first, as above.

### Tests

```bash
(cd backend && pip install -r requirements-dev.txt && pytest)
(cd frontend && npm test)
```

To run the backend suite against Postgres, use a separate database whose name ends in `_test`; the suite drops its tables.

```bash
docker exec conversate-postgres createdb -U conversate conversate_test
(cd backend && TEST_DATABASE_URL=postgresql://conversate:conversate@127.0.0.1:5432/conversate_test pytest)
```

### Lint & format

```bash
(cd backend && ruff check . && ruff format .)
(cd frontend && npm run lint && npm run format)
```

---

## API

All `/api` endpoints require an Auth0 access token (`Authorization: Bearer <token>`).
Translation and speech endpoints are limited to 30 requests per minute per user.

### Account

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/me` | Get your profile and progress |
| POST | `/api/me` | Create your profile with a username |
| PUT | `/api/me` | Change your username |
| DELETE | `/api/me` | Delete your profile and progress |
| POST | `/api/me/lessons/<id>` | Mark a lesson complete |
| POST | `/api/me/reset` | Reset your progress (keeps your username) |
| GET | `/api/usernames/<username>` | Check whether a username is valid and available |

### Quiz

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/me/quiz/start` | Start a timed quiz and get its questions; send `{"practice": true}` for an untimed one |
| POST | `/api/me/quiz/answer` | Answer the current question |
| POST | `/api/me/quiz/pause` | Pause the quiz timer (once per quiz; timed quizzes only) |
| POST | `/api/me/quiz/resume` | Resume the quiz timer |
| POST | `/api/me/quiz/submit` | Finish the quiz and save a new best (practice results aren't saved) |
| GET | `/api/leaderboard` | Top 100 quiz scores |

### Translation & speech

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/translate` | Translate text between English and Italian |
| POST | `/api/tts` | Turn text into speech |
| POST | `/api/stt` | Turn recorded speech into text |

### Health

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Health check (no token needed) |

---

## Credits

Icons by [Icons8](https://icons8.com).
