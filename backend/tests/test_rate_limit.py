TRANSLATE = ('/api/translate', {'text': 'ciao', 'source': 'it', 'target': 'en'})
TTS = ('/api/tts', {'text': 'ciao', 'language': 'it'})
STT = (
    '/api/stt',
    {'audio': 'ZmFrZS1hdWRpbw==', 'mime_type': 'audio/webm;codecs=opus', 'language': 'it'},
)


def test_translation_and_speech_share_one_limit(rate_limited_client, auth_headers, google_stub):
    headers = auth_headers(sub='auth0|ratelimit')
    # One response that satisfies all three endpoints.
    google_stub.respond(
        {
            'data': {'translations': [{'translatedText': 'hello'}]},
            'audioContent': 'YXVkaW8=',
            'results': [{'alternatives': [{'transcript': 'ciao'}]}],
        }
    )

    for url, body in [TRANSLATE, TTS, STT] * 10:
        response = rate_limited_client.post(url, json=body, headers=headers)
        assert response.status_code == 200

    for url, body in [TRANSLATE, TTS, STT]:
        response = rate_limited_client.post(url, json=body, headers=headers)
        assert response.status_code == 429
