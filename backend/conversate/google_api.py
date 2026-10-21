import json
import urllib.error
import urllib.request

from flask import current_app

TRANSLATE_URL = 'https://translation.googleapis.com/language/translate/v2'
TTS_URL = 'https://texttospeech.googleapis.com/v1/text:synthesize'
STT_URL = 'https://speech.googleapis.com/v1/speech:recognize'

GOOGLE_API_TIMEOUT_SECONDS = 8


class GoogleServiceError(Exception):
    pass


def post(base_url, payload):
    # The key goes in a header rather than the ?key= query string so it
    # never ends up in URL logs (access logs, proxies, browser history).
    req = urllib.request.Request(
        base_url, data=json.dumps(payload).encode(),
        headers={
            'Content-Type': 'application/json',
            'X-goog-api-key': current_app.config['GOOGLE_CLOUD_API_KEY'],
        },
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=GOOGLE_API_TIMEOUT_SECONDS) as r:
            return json.loads(r.read())
    except (urllib.error.URLError, TimeoutError, ValueError) as e:
        raise GoogleServiceError(str(e)) from e
