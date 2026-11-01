import functools
import time

import jwt
from flask import current_app, g, jsonify, request
from jwt import PyJWKClient, PyJWKClientConnectionError

JWKS_TIMEOUT_SECONDS = 5
# One retry for a key download that fails fast, such as a connection reset
# just after a restart. A timeout isn't retried; it has already waited.
JWKS_RETRY_DELAY_SECONDS = 1
# Keys are cached an hour (PyJWT's default is 5 minutes), so a key Auth0
# revokes is trusted no longer than that.
JWKS_CACHE_SECONDS = 60 * 60


# Made once, so its key cache lasts across requests.
@functools.cache
def _jwks_client(domain):
    return PyJWKClient(
        f'https://{domain}/.well-known/jwks.json',
        timeout=JWKS_TIMEOUT_SECONDS,
        lifespan=JWKS_CACHE_SECONDS,
    )


def _timed_out(error):
    cause = error.__cause__
    return isinstance(cause, TimeoutError) or isinstance(
        getattr(cause, 'reason', None), TimeoutError
    )


def _signing_key(domain, token):
    client = _jwks_client(domain)
    try:
        return client.get_signing_key_from_jwt(token)
    except PyJWKClientConnectionError as e:
        if _timed_out(e):
            raise
        current_app.logger.info(
            'JWKS fetch failed, retrying in %ss: %s', JWKS_RETRY_DELAY_SECONDS, e
        )
        time.sleep(JWKS_RETRY_DELAY_SECONDS)
    return client.get_signing_key_from_jwt(token)


def _verify_token():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    token = auth_header[7:]
    domain = current_app.config['AUTH0_DOMAIN']
    audience = current_app.config['AUTH0_AUDIENCE']
    signing_key = _signing_key(domain, token)
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=['RS256'],
        audience=audience,
        issuer=f'https://{domain}/',
        # Allow a minute of clock difference with Auth0.
        leeway=60,
        # PyJWT checks exp only when it's present; Auth0 always sends these.
        options={'require': ['exp', 'iat', 'sub']},
    )


def require_auth(f):
    @functools.wraps(f)
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
        g.current_user_sub = claims['sub']
        return f(*args, **kwargs)

    return decorated
