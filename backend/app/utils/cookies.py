import secrets

from fastapi import Response

from app.core.config import get_settings


def apply_auth_cookies(response: Response, access_token: str) -> str:
    settings = get_settings()
    csrf_token = secrets.token_urlsafe(24)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        domain=settings.cookie_domain,
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,
        secure=settings.cookie_secure,
        samesite="lax",
        domain=settings.cookie_domain,
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )
    return csrf_token


def clear_auth_cookies(response: Response) -> None:
    settings = get_settings()
    response.delete_cookie("access_token", path="/", domain=settings.cookie_domain)
    response.delete_cookie("csrf_token", path="/", domain=settings.cookie_domain)
