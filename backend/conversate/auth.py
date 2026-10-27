from functools import wraps

import jwt
from flask import current_app, g, jsonify, request
from jwt import PyJWKClient, PyJWKClientConnectionError

JWKS_TIMEOUT_SECONDS = 5
# A token with an unknown key ID forces a key refresh, which anyone can
# trigger with a forged token; this caps how often that re-downloads.
JWKS_REFRESH_COOLDOWN_SECONDS = 60
# Keep keys 10 hours (PyJWT's default is 5 minutes), so fewer downloads can
# fail a sign-in. A new key is fetched when first used, subject to the cooldown;
# a key Auth0 removes stays trusted until the cache expires.
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
        # Allow a minute of clock difference with Auth0.
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
