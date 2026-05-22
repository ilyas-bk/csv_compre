import secrets

from django.conf import settings
from django.http import HttpResponse

OWNER_COOKIE = "csv_compare_owner"
OWNER_COOKIE_MAX_AGE = 365 * 24 * 60 * 60


def resolve_owner_key(request) -> tuple[str, bool]:
    """Return the browser's owner key, generating one if missing."""
    existing = request.COOKIES.get(OWNER_COOKIE)
    if existing:
        return existing, False
    return secrets.token_urlsafe(32), True


def set_owner_cookie(response: HttpResponse, owner_key: str) -> None:
    response.set_cookie(
        OWNER_COOKIE,
        owner_key,
        max_age=OWNER_COOKIE_MAX_AGE,
        httponly=True,
        samesite="Lax",
        secure=not settings.DEBUG,
    )


def attach_owner_cookie(request, response: HttpResponse) -> HttpResponse:
    owner_key, is_new = resolve_owner_key(request)
    if is_new:
        set_owner_cookie(response, owner_key)
    return response


def is_room_owner(request, room) -> bool:
    owner_key = request.COOKIES.get(OWNER_COOKIE)
    return bool(owner_key) and room.owner_key == owner_key
