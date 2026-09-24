from flask import Blueprint, jsonify, current_app

from .. import google_api
from ..auth import require_auth
from .common import _json_body

speech_bp = Blueprint('speech_bp', __name__)

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
def translate_text():
    body = _json_body()
    if body is None:
        return jsonify(error='Request body must be a JSON object'), 400
    text = (body.get('text') or '').strip()
    source = body.get('source')
    target = body.get('target')
    if not text or len(text) > MAX_TRANSLATE_TEXT_LENGTH:
        return jsonify(
            error='text is required and must be at most %d characters' % MAX_TRANSLATE_TEXT_LENGTH
        ), 400
    if source not in TRANSLATE_LANGUAGES or target not in TRANSLATE_LANGUAGES:
        return jsonify(
            error='source and target must be one of: %s' % ', '.join(sorted(TRANSLATE_LANGUAGES))
        ), 400

    try:
        data = google_api.post(google_api.TRANSLATE_URL, {
            'q': text,
            'source': source,
            'target': target,
            'format': 'text',
        })
        translated = data['data']['translations'][0]['translatedText']
    except (google_api.GoogleServiceError, KeyError, IndexError, TypeError) as e:
        current_app.logger.warning('Translation request failed: %s', e)
        return jsonify(error='Translation service unavailable'), 502

    return jsonify(translatedText=translated), 200


@speech_bp.route('/api/tts', methods=['POST'])
@require_auth
def synthesize_speech():
    body = _json_body()
    if body is None:
        return jsonify(error='Request body must be a JSON object'), 400
    text = (body.get('text') or '').strip()
    voice = TTS_VOICES.get(body.get('language'))
    if not text or len(text.encode('utf-8')) > MAX_TTS_TEXT_LENGTH:
        return jsonify(
            error='text is required and must be at most %d characters' % MAX_TTS_TEXT_LENGTH
        ), 400
    if voice is None:
        return jsonify(
            error='language must be one of: %s' % ', '.join(sorted(TTS_VOICES))
        ), 400

    try:
        data = google_api.post(google_api.TTS_URL, {
            'input': {'text': text},
            'voice': voice,
            'audioConfig': {'audioEncoding': 'MP3'},
        })
        audio_content = data['audioContent']
    except (google_api.GoogleServiceError, KeyError, TypeError) as e:
        current_app.logger.warning('Speech synthesis request failed: %s', e)
        return jsonify(error='Speech synthesis service unavailable'), 502

    return jsonify(audioContent=audio_content), 200


@speech_bp.route('/api/stt', methods=['POST'])
@require_auth
def transcribe_speech():
    body = _json_body()
    if body is None:
        return jsonify(error='Request body must be a JSON object'), 400
    audio_b64 = body.get('audio')
    encoding = STT_ENCODINGS.get(body.get('mimeType'))
    language_code = STT_LANGUAGES.get(body.get('language'))
    if not audio_b64 or encoding is None or language_code is None:
        return jsonify(error='audio, a supported mimeType, and language are required'), 400
    if len(audio_b64) > MAX_STT_AUDIO_BYTES * 4 // 3:
        return jsonify(error='audio is too large'), 400

    try:
        data = google_api.post(google_api.STT_URL, {
            'config': {'encoding': encoding, 'languageCode': language_code},
            'audio': {'content': audio_b64},
        })
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
