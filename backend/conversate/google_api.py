import httpx
from flask import current_app

TRANSLATE_URL = 'https://translation.googleapis.com/language/translate/v2'
TTS_URL = 'https://texttospeech.googleapis.com/v1/text:synthesize'
STT_URL = 'https://speech.googleapis.com/v1/speech:recognize'

GOOGLE_API_TIMEOUT_SECONDS = 8

# Speech-to-text replies only after transcribing the whole clip (up to the
# frontend's 30-second recording cap), so it gets longer to answer. The
# frontend's timeout for this call (api/stt.js) must stay above these, or the
# browser gives up first.
STT_TIMEOUT = httpx.Timeout(GOOGLE_API_TIMEOUT_SECONDS, read=20)

# One client for the whole process, so calls reuse open connections instead
# of paying for a new TCP + TLS handshake to Google every time. httpx.Client
# is safe to share across Gunicorn's worker threads.
#
# httpx closes idle connections after 5 seconds by default; keep them for a
# minute so calls a few seconds apart still reuse one. A Limits() object
# defaults its connection caps to unlimited, so restate the client's usual
# caps (100 total, 20 idle) to change only the expiry.
_client = httpx.Client(
    timeout=GOOGLE_API_TIMEOUT_SECONDS,
    limits=httpx.Limits(max_connections=100, max_keepalive_connections=20, keepalive_expiry=60),
)


class GoogleServiceError(Exception):
    pass


def post(base_url, payload, timeout=httpx.USE_CLIENT_DEFAULT):
    try:
        # The key goes in a header rather than the ?key= query string so it
        # never ends up in URL logs (access logs, proxies, browser history).
        response = _client.post(
            base_url,
            json=payload,
            headers={'X-goog-api-key': current_app.config['GOOGLE_CLOUD_API_KEY']},
            timeout=timeout,
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        # The error body carries Google's actual reason (e.g. a bad API key
        # or an invalid parameter); the status line alone is just "403".
        raise GoogleServiceError(f'{e}: {e.response.text}') from e
    except (httpx.HTTPError, ValueError) as e:
        raise GoogleServiceError(str(e)) from e
