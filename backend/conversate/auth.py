import json
import time
import urllib.request
from functools import wraps
from flask import request, jsonify, current_app, g
import jwt
from jwt import PyJWTError

_jwks_cache = {}
_jwks_last_fetch = {}

JWKS_TIMEOUT_SECONDS = 5
# A forced refresh is normally triggered by a token naming an unknown key ID.
# An attacker can trigger that for free on every request with a forged kid,
# so this cooldown caps how often a single domain's keys are re-downloaded
# regardless of how many such requests arrive.
JWKS_REFRESH_COOLDOWN_SECONDS = 60


class JwksUnavailable(Exception):
    pass


def _get_jwks(domain, force_refresh=False):
    last_fetch = _jwks_last_fetch.get(domain, 0)
    on_cooldown = (time.monotonic() - last_fetch) < JWKS_REFRESH_COOLDOWN_SECONDS
    if domain not in _jwks_cache or (force_refresh and not on_cooldown):
        url = f'https://{domain}/.well-known/jwks.json'
        try:
            with urllib.request.urlopen(url, timeout=JWKS_TIMEOUT_SECONDS) as r:
                _jwks_cache[domain] = json.loads(r.read())
            _jwks_last_fetch[domain] = time.monotonic()
        except Exception as e:
            raise JwksUnavailable(str(e)) from e
    return _jwks_cache[domain]


def _signing_key(domain, kid):
    jwks = _get_jwks(domain)
    for key in jwks.get('keys', []):
        if key.get('kid') == kid:
            return key
    jwks = _get_jwks(domain, force_refresh=True)
    for key in jwks.get('keys', []):
        if key.get('kid') == kid:
            return key
    return None


def _verify_token():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    token = auth_header[7:]
    domain = current_app.config['AUTH0_DOMAIN']
    audience = current_app.config['AUTH0_AUDIENCE']
    kid = jwt.get_unverified_header(token).get('kid')
    jwk = _signing_key(domain, kid)
    if jwk is None:
        raise PyJWTError('no signing key matches token kid %r' % kid)
    signing_key = jwt.PyJWK(jwk).key
    return jwt.decode(token, signing_key, algorithms=['RS256'], audience=audience,
                      issuer=f'https://{domain}/')


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            claims = _verify_token()
        except JwksUnavailable as e:
            current_app.logger.warning('JWKS fetch failed: %s', e)
            return jsonify(error='Authentication service unavailable'), 503
        except Exception:
            return jsonify(error='Unauthorized'), 401
        if claims is None or not claims.get('sub'):
            return jsonify(error='Unauthorized'), 401
        g.jwt_claims = claims
        g.current_user_sub = claims['sub']
        return f(*args, **kwargs)
    return decorated
