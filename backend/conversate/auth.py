from functools import wraps

import jwt
from flask import current_app, g, jsonify, request
from jwt import PyJWKClient, PyJWKClientConnectionError

JWKS_TIMEOUT_SECONDS = 5
# A forced refresh is normally triggered by a token naming an unknown key ID.
# An attacker can trigger that for free on every request with a forged kid,
# so this cooldown caps how often a single domain's keys are re-downloaded
# regardless of how many such requests arrive.
JWKS_REFRESH_COOLDOWN_SECONDS = 60
# Each re-download is a chance for a network blip to fail a sign-in, so keep
# the keys for 10 hours rather than PyJWT's 5 minutes. A new key is still
# fetched when a token first uses it (subject to the cooldown above), but a key
# Auth0 removes stays trusted until the cache expires.
JWKS_CACHE_SECONDS = 10 * 60 * 60

# One client per Auth0 domain, each caching that domain's keys.
_jwks_clients = {}


def _jwks_client(domain):
    if domain not in _jwks_clients:
        _jwks_clients[domain] = PyJWKClient(
            f'https://{domain}/.well-known/jwks.json',
            timeout=JWKS_TIMEOUT_SECONDS,
            lifespan=JWKS_CACHE_SECONDS,
            cooldown_duration=JWKS_REFRESH_COOLDOWN_SECONDS,
        )
    return _jwks_clients[domain]


def _verify_token():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    token = auth_header[7:]
    domain = current_app.config['AUTH0_DOMAIN']
    audience = current_app.config['AUTH0_AUDIENCE']
    signing_key = _jwks_client(domain).get_signing_key_from_jwt(token)
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=['RS256'],
        audience=audience,
        issuer=f'https://{domain}/',
        # Tolerate small clock differences between this server and Auth0's —
        # without it, a token's iat/exp can fail validation purely from
        # clock skew, with no actual timing problem.
        leeway=60,
    )


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            claims = _verify_token()
        except PyJWKClientConnectionError as e:
            current_app.logger.warning('JWKS fetch failed: %s', e)
            return jsonify(error='Authentication service unavailable'), 503
        except jwt.PyJWTError as e:
            current_app.logger.info('Rejected token: %s', e)
            return jsonify(error='Unauthorized'), 401
        if claims is None or not claims.get('sub'):
            return jsonify(error='Unauthorized'), 401
        g.jwt_claims = claims
        g.current_user_sub = claims['sub']
        return f(*args, **kwargs)

    return decorated
