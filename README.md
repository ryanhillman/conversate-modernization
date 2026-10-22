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

## [Demo](https://youtu.be/GpFT1M0YnfY)

---

## Screenshot

![Conversate Screenshot](./docs/screenshot.png)

---

## Features

Secure profile handling with the ability to link Google Accounts.

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
- PostgreSQL
- Gunicorn 26.0

**Frontend**
- Vue.js 3
- Vite 8.1
- Vue Router 4
- Bootstrap 5
- CSS

**Authentication**
- Auth0
- PyJWT 2.15

---

## How to Run

Requires Python 3.14, Node 22, Auth0, and Google Cloud.

### Auth0

Create an Auth0 Single Page Application and an Auth0 API:

- Add `http://localhost:3000` to Allowed Callback URLs, Logout URLs, and Web Origins.
- API set an identifier (e.g. `https://conversate-api`) — this becomes the audience used by both frontend and backend.
- Enable **Allow Offline Access** on the API, so refresh tokens are issued and expired sessions can silently renew instead of getting stuck.

Create `frontend/.env`:

```
VITE_AUTH0_DOMAIN=<your Auth0 domain>
VITE_AUTH0_CLIENT_ID=<your SPA client ID>
VITE_AUTH0_AUDIENCE=<your API identifier>
```

Set the same domain/audience in `backend/.env` (`AUTH0_DOMAIN`, `AUTH0_AUDIENCE`).

### Google Cloud API

Translation, text-to-speech, and speech-to-text call the Google Cloud APIs directly with a plain API key.

- Create a project in Google Cloud Console.
- Enable the Translation, Text-to-Speech, and Speech-to-Text APIs.
- Create an API key (APIs & Services → Credentials).
- Set it as `GOOGLE_CLOUD_API_KEY` in `backend/.env`.

### Backend

Create `backend/.env`:

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
venv\Scripts\activate #macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
flask --app run.py db upgrade
python run.py
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

#### Postgres test

```bash
docker exec conversate-postgres createdb -U conversate conversate_test
# never point this at the app's own database — the suite drops its tables
TEST_DATABASE_URL=postgresql://conversate:conversate@127.0.0.1:5432/conversate_test pytest
```

---

## Credits

Icons by [Icons8](https://icons8.com).
