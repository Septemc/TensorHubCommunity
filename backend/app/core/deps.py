from collections.abc import AsyncGenerator

from fastapi import Cookie, Depends, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import decode_access_token
from app.db.session import async_session_maker
from app.models.user import User


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    access_token: str | None = Cookie(default=None),
) -> User:
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = decode_access_token(access_token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token") from exc
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")
    result = await db.execute(
        select(User)
        .options(selectinload(User.roles))
        .where(User.id == int(user_id), User.status == 1)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


async def get_optional_user(
    db: AsyncSession = Depends(get_db),
    access_token: str | None = Cookie(default=None),
) -> User | None:
    if not access_token:
        return None
    try:
        payload = decode_access_token(access_token)
        user_id = int(payload.get("sub"))
    except Exception:
        return None
    result = await db.execute(
        select(User).options(selectinload(User.roles)).where(User.id == user_id, User.status == 1)
    )
    return result.scalar_one_or_none()


def require_csrf(request: Request, csrf_token: str | None = Cookie(default=None), x_csrf_token: str | None = Header(default=None)) -> None:
    if request.method in {"GET", "HEAD", "OPTIONS"}:
        return
    if not csrf_token or not x_csrf_token or csrf_token != x_csrf_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid CSRF token")


def require_verified_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.verification_status != "approved":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verification required")
    return current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.has_role("admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return current_user


def require_moderator(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.has_any_role({"admin", "super_moderator", "moderator"}):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Moderator role required")
    return current_user
