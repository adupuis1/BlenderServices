import time
import uuid
from dataclasses import dataclass

import httpx 
import jwt
from jwt import PyJWKClient

from common.config import settings

ALGORITHMS = ["RS256"]
JWLS_URL = f"{settings.LOGIN_SERVICE_URL}/.well-known/jwks.json"

_client: PyJWKClient | None = None
_fetched_at: float = 0.0

class InvalidToken(Exception):
    pass

@dataclass(frozen=True)
class Caller:
    id: uuid.UUID
    username: str | None
    is_superuser: bool

def _jwks() -> PyJWKClient:
    """One client, refreshed occasionally so key rotation is picked up."""
    global _client, _fetched_at
    now = time.monotonic()
    if _client is None or now - _fetched_at > settings.JWKS_CACHE_SECONDS:
        _client = PyJWKClient(JWLS_URL, cache_keys=True)
        _fetched_at = now
    return _client

def caller_from_token(token: str) -> Caller:
    try:
        key = _jwks().get_signing_key_from_jwt(token).key
    except (jwt.PyJWKClientError, httpx.HTTPError) as exc:
        raise InvalidToken(f"Could not fetch signing keys: {exc}") from exc
    
    try:
        claims = jwt.decode(
            token,
            key,
            algorithms=ALGORITHMS,
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
            options={"require": ["exp", "iss", "aud", "sub"]},
        )
    except jwt.InvalidTokenError as exc:
        raise InvalidToken(str(exc)) from exc

    try:
        return Caller(
            id=uuid.UUID(claims["sub"]),
            username=claims.get("username"),
            is_superuser=bool(claims.get("is_superuser", False)),
        )
    except (KeyError, ValueError) as exc:
        raise InvalidToken("Token subject is not a user id") from exc
