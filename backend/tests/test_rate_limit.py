import pytest

TRANSLATE = ('/api/translate', {'text': 'ciao', 'source': 'it', 'target': 'en'})
TTS = ('/api/tts', {'text': 'ciao', 'language': 'it'})
STT = (
    '/api/stt',
    {'audio': 'ZmFrZS1hdWRpbw==', 'mime_type': 'audio/webm;codecs=opus', 'language': 'it'},
)


@pytest.mark.rate_limited
def test_translation_and_speech_share_one_limit_per_user(client, auth_headers, google_stub):
    headers = auth_headers()
    # One response that satisfies all three endpoints.
    google_stub.respond(
        {
            'data': {'translations': [{'translatedText': 'hello'}]},
            'audioContent': 'YXVkaW8=',
            'results': [{'alternatives': [{'transcript': 'ciao'}]}],
        }
    )

    for url, body in [TRANSLATE, TTS, STT] * 10:
        response = client.post(url, json=body, headers=headers)
        assert response.status_code == 200

    for url, body in [TRANSLATE, TTS, STT]:
        response = client.post(url, json=body, headers=headers)
        assert response.status_code == 429

    # Counted per account, not per address: another user on the same
    # connection isn't limited.
    url, body = TRANSLATE
    other = auth_headers(sub='auth0|other')
    assert client.post(url, json=body, headers=other).status_code == 200
