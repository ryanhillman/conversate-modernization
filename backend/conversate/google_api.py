import httpx
from flask import current_app

TRANSLATE_URL = 'https://translation.googleapis.com/language/translate/v2'
TTS_URL = 'https://texttospeech.googleapis.com/v1/text:synthesize'
STT_URL = 'https://speech.googleapis.com/v1/speech:recognize'

GOOGLE_API_TIMEOUT_SECONDS = 8

# One client for the whole process, so calls reuse open connections instead
# of paying for a new TCP + TLS handshake to Google every time. httpx.Client
# is safe to share across Gunicorn's worker threads.
_client = httpx.Client(timeout=GOOGLE_API_TIMEOUT_SECONDS)


class GoogleServiceError(Exception):
    pass


def post(base_url, payload):
    try:
        # The key goes in a header rather than the ?key= query string so it
        # never ends up in URL logs (access logs, proxies, browser history).
        response = _client.post(
            base_url,
            json=payload,
            headers={'X-goog-api-key': current_app.config['GOOGLE_CLOUD_API_KEY']},
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        # The error body carries Google's actual reason (e.g. a bad API key
        # or an invalid parameter); the status line alone is just "403".
        raise GoogleServiceError(f'{e}: {e.response.text}') from e
    except (httpx.HTTPError, ValueError) as e:
        raise GoogleServiceError(str(e)) from e
