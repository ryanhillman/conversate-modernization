from flask import Blueprint, current_app, jsonify

from .. import google_api
from ..auth import require_auth
from ..extensions import limiter
from .common import json_body, str_field

speech_bp = Blueprint('speech_bp', __name__)

# Each of these endpoints calls a paid Google Cloud API; without a limit, an
# Auth0 account (free to create) can run up the bill without restriction.
GOOGLE_API_RATE_LIMIT = '30 per minute'

TRANSLATE_LANGUAGES = frozenset({'en', 'it'})
MAX_TRANSLATE_TEXT_LENGTH = 5000
TTS_VOICES = {
    'en': {'languageCode': 'en-US', 'name': 'en-US-Wavenet-D'},
    'it': {'languageCode': 'it-IT', 'name': 'it-IT-Wavenet-A'},
}
MAX_TTS_TEXT_LENGTH = 5000  # bytes; Cloud Text-to-Speech's synchronous synthesize limit
STT_LANGUAGES = {'en': 'en-US', 'it': 'it-IT'}
STT_ENCODINGS = {'audio/webm;codecs=opus': 'WEBM_OPUS'}
MAX_STT_AUDIO_BYTES = 1_000_000


@speech_bp.route('/api/translate', methods=['POST'])
@require_auth
@limiter.limit(GOOGLE_API_RATE_LIMIT)
def translate_text():
    body = json_body()
    if body is None:
        return jsonify(error='Request body must be a JSON object'), 400
    text = str_field(body, 'text')
    source = str_field(body, 'source')
    target = str_field(body, 'target')
    if not text or len(text) > MAX_TRANSLATE_TEXT_LENGTH:
        return jsonify(
            error=f'text is required and must be at most {MAX_TRANSLATE_TEXT_LENGTH} characters'
        ), 400
    if source not in TRANSLATE_LANGUAGES or target not in TRANSLATE_LANGUAGES:
        return jsonify(
            error=f'source and target must be one of: {", ".join(sorted(TRANSLATE_LANGUAGES))}'
        ), 400

    try:
        data = google_api.post(
            google_api.TRANSLATE_URL,
            {
                'q': text,
                'source': source,
                'target': target,
                'format': 'text',
            },
        )
        translated = data['data']['translations'][0]['translatedText']
    except (google_api.GoogleServiceError, KeyError, IndexError, TypeError) as e:
        current_app.logger.warning('Translation request failed: %s', e)
        return jsonify(error='Translation service unavailable'), 502

    return jsonify(translated_text=translated), 200


@speech_bp.route('/api/tts', methods=['POST'])
@require_auth
@limiter.limit(GOOGLE_API_RATE_LIMIT)
def synthesize_speech():
    body = json_body()
    if body is None:
        return jsonify(error='Request body must be a JSON object'), 400
    text = str_field(body, 'text')
    voice = TTS_VOICES.get(str_field(body, 'language'))
    if not text or len(text.encode('utf-8')) > MAX_TTS_TEXT_LENGTH:
        return jsonify(
            error=f'text is required and must be at most {MAX_TTS_TEXT_LENGTH} characters'
        ), 400
    if voice is None:
        return jsonify(error=f'language must be one of: {", ".join(sorted(TTS_VOICES))}'), 400

    try:
        data = google_api.post(
            google_api.TTS_URL,
            {
                'input': {'text': text},
                'voice': voice,
                'audioConfig': {'audioEncoding': 'MP3'},
            },
        )
        audio_content = data['audioContent']
    except (google_api.GoogleServiceError, KeyError, TypeError) as e:
        current_app.logger.warning('Speech synthesis request failed: %s', e)
        return jsonify(error='Speech synthesis service unavailable'), 502

    return jsonify(audio_content=audio_content), 200


@speech_bp.route('/api/stt', methods=['POST'])
@require_auth
@limiter.limit(GOOGLE_API_RATE_LIMIT)
def transcribe_speech():
    body = json_body()
    if body is None:
        return jsonify(error='Request body must be a JSON object'), 400
    audio_b64 = str_field(body, 'audio')
    encoding = STT_ENCODINGS.get(str_field(body, 'mime_type'))
    language_code = STT_LANGUAGES.get(str_field(body, 'language'))
    if not audio_b64 or encoding is None or language_code is None:
        return jsonify(error='audio, a supported mime_type, and language are required'), 400
    if len(audio_b64) > MAX_STT_AUDIO_BYTES * 4 // 3:
        return jsonify(error='audio is too large'), 400

    try:
        data = google_api.post(
            google_api.STT_URL,
            {
                'config': {'encoding': encoding, 'languageCode': language_code},
                'audio': {'content': audio_b64},
            },
            timeout=google_api.STT_TIMEOUT,
        )
    except google_api.GoogleServiceError as e:
        current_app.logger.warning('Transcription request failed: %s', e)
        return jsonify(error='Speech recognition service unavailable'), 502

    results = data.get('results') or []
    if not results:
        return jsonify(error='No speech detected'), 422
    try:
        transcript = results[0]['alternatives'][0]['transcript']
    except (KeyError, IndexError, TypeError) as e:
        current_app.logger.warning('Unexpected transcription response shape: %s', e)
        return jsonify(error='Speech recognition service unavailable'), 502

    return jsonify(transcript=transcript), 200
