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
- SQLAlchemy 2.0
- Flask-Migrate 4.1 + Alembic 1.18
- Flask-SQLAlchemy 3.1
- Flask-Limiter 4.1
- httpx 0.28
- PostgreSQL 18
- Gunicorn 26.0
- Docker

**Frontend**
- Vue.js 3.5
- Vite 8.3
- Vue Router 4.6
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

Requires Python 3.14, Node 22, Docker, Auth0, and Google Cloud.

### Auth0

Create an Auth0 Single Page Application and an Auth0 API:

- Add `http://localhost:3000` to Allowed Callback URLs, Logout URLs, and Web Origins.
- API set an identifier (e.g. `https://conversate-api`) — this becomes the audience used by both frontend and backend.
- Enable **Allow Offline Access** on the API, so refresh tokens are issued and expired sessions can silently renew instead of getting stuck.
- Enable **Refresh Token Rotation** on the SPA; the frontend uses refresh tokens, and Auth0 only issues them to browser apps with rotation on.
- Enable the **Refresh Token** grant type on the SPA (Advanced Settings → Grant Types), which rotation requires.

Copy `frontend/.env.example` to `frontend/.env` and fill in your values:

```
VITE_AUTH0_DOMAIN=<your Auth0 domain>
VITE_AUTH0_CLIENT_ID=<your SPA client ID>
VITE_AUTH0_AUDIENCE=<your API identifier>
```

Set the same domain/audience in `backend/.env` (`AUTH0_DOMAIN`, `AUTH0_AUDIENCE`).

### Google Cloud API

Translation, text-to-speech, and speech-to-text call the Google Cloud APIs directly with a plain API key.

- Create a project in Google Cloud Console.
- Enable billing on the project; all three APIs require it, even within their free tiers.
- Enable the Translation, Text-to-Speech, and Speech-to-Text APIs.
- Create an API key (APIs & Services → Credentials).
- Set it as `GOOGLE_CLOUD_API_KEY` in `backend/.env`.

### Backend

Copy `backend/.env.example` to `backend/.env` and fill in your values:

```
DATABASE_URL=postgresql://conversate:conversate@127.0.0.1:5432/conversate
AUTH0_DOMAIN=<your Auth0 domain>
AUTH0_AUDIENCE=<your API identifier>
GOOGLE_CLOUD_API_KEY=<your Google Cloud API key>
DEBUG=False
```

Start a local Postgres (Docker):

```bash
docker run -d --name conversate-postgres -p 5432:5432 -e POSTGRES_USER=conversate -e POSTGRES_PASSWORD=conversate -e POSTGRES_DB=conversate postgres:18
```

#### Start backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
flask --app run.py db upgrade
python run.py  # macOS: if this fails to bind, disable AirPlay Receiver (System Settings → General → AirDrop & Handoff) — it also uses port 5000
```

#### Docker

```bash
docker build -t conversate-backend backend
docker run -p 5000:5000 --env-file backend/.env conversate-backend
# inside the container, 127.0.0.1 is the container itself — use host.docker.internal
# instead of 127.0.0.1 in DATABASE_URL to reach the Postgres on your machine
# migrations don't run automatically — run `flask --app run.py db upgrade` separately first
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest
```

```bash
cd frontend
npm test
```

#### Postgres test

```bash
docker exec conversate-postgres createdb -U conversate conversate_test
# never point this at the app's own database — the suite drops its tables
TEST_DATABASE_URL=postgresql://conversate:conversate@127.0.0.1:5432/conversate_test pytest
```

### Lint & format

```bash
# Backend
ruff check .
ruff format .

# Frontend
npm run lint
npm run format
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
| POST | `/api/me/quiz/start` | Start a timed quiz and get its questions |
| POST | `/api/me/quiz/answer` | Answer the current question |
| POST | `/api/me/quiz/pause` | Pause the quiz timer (once per quiz) |
| POST | `/api/me/quiz/resume` | Resume the quiz timer |
| POST | `/api/me/quiz/submit` | Finish the quiz and save a new best |
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
