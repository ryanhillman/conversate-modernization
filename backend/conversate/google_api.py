import httpx
from flask import current_app

TRANSLATE_URL = 'https://translation.googleapis.com/language/translate/v2'
TTS_URL = 'https://texttospeech.googleapis.com/v1/text:synthesize'
STT_URL = 'https://speech.googleapis.com/v1/speech:recognize'

GOOGLE_API_TIMEOUT_SECONDS = 8

# Speech-to-text answers only after transcribing the whole clip (up to 30
# seconds), so it gets longer. api/stt.js's timeout must stay above these.
STT_TIMEOUT = httpx.Timeout(GOOGLE_API_TIMEOUT_SECONDS, read=20)

# One shared client, so calls reuse connections to Google.
_client = httpx.Client(timeout=GOOGLE_API_TIMEOUT_SECONDS)


class GoogleServiceError(Exception):
    pass


def post(url, payload, timeout=httpx.USE_CLIENT_DEFAULT):
    try:
        # In a header, not ?key=, so the key stays out of URL logs.
        response = _client.post(
            url,
            json=payload,
            headers={'X-goog-api-key': current_app.config['GOOGLE_CLOUD_API_KEY']},
            timeout=timeout,
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        # The body has Google's reason; the status line alone is just "403".
        raise GoogleServiceError(f'{e}: {e.response.text}') from e
    except (httpx.HTTPError, ValueError) as e:
        raise GoogleServiceError(str(e)) from e
