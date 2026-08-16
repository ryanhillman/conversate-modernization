import json
import urllib.error
import urllib.parse
import urllib.request

from flask import current_app

TRANSLATE_URL = 'https://translation.googleapis.com/language/translate/v2'
TTS_URL = 'https://texttospeech.googleapis.com/v1/text:synthesize'
STT_URL = 'https://speech.googleapis.com/v1/speech:recognize'

GOOGLE_API_TIMEOUT_SECONDS = 8


class GoogleServiceError(Exception):
    pass


def post(base_url, payload):
    url = base_url + '?key=' + urllib.parse.quote(current_app.config['GOOGLE_CLOUD_API_KEY'])
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={'Content-Type': 'application/json'}, method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=GOOGLE_API_TIMEOUT_SECONDS) as r:
            return json.loads(r.read())
    except (urllib.error.URLError, TimeoutError, ValueError) as e:
        raise GoogleServiceError(str(e)) from e
