from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_current_user, get_db, get_optional_user, require_admin, require_csrf
from app.core.security import create_access_token, hash_password, verify_password
from app.models import Role, User
from app.schemas.common import MessageResponse
from app.schemas.user import (
    RoleAssignment,
    SessionResponse,
    UserLogin,
    UserProfileUpdate,
    UserRead,
    UserRegister,
    VerificationUpdate,
)
from app.utils.cookies import apply_auth_cookies, clear_auth_cookies

router = APIRouter()


async def _load_user_with_roles(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).options(selectinload(User.roles)).where(User.id == user_id))
    return result.scalar_one_or_none()


@router.post('/register', response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister, db: AsyncSession = Depends(get_db)) -> User:
    existing = await db.execute(
        select(User).where(
            or_(User.username == payload.username, User.student_id == payload.student_id, User.email == payload.email)
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail='Username, student ID, or email already exists')
    member_role = await db.execute(select(Role).where(Role.name == 'member'))
    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        email=payload.email,
        real_name=payload.real_name,
        gender=payload.gender,
        major=payload.major,
        student_id=payload.student_id,
        verification_status='pending',
        roles=[member_role.scalar_one()],
    )
    db.add(user)
    await db.commit()
    fresh_user = await _load_user_with_roles(db, user.id)
    if not fresh_user:
        raise HTTPException(status_code=500, detail='Failed to load created user')
    return fresh_user


@router.post('/login')
async def login(payload: UserLogin, response: Response, db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(
        select(User)
        .options(selectinload(User.roles))
        .where(or_(User.username == payload.identifier, User.email == payload.identifier))
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=400, detail='Invalid credentials')
    if user.status != 1:
        raise HTTPException(status_code=403, detail='Account disabled')
    user.last_login = datetime.now(timezone.utc)
    token = create_access_token(str(user.id))
    csrf_token = apply_auth_cookies(response, token)
    await db.commit()
    fresh_user = await _load_user_with_roles(db, user.id)
    if not fresh_user:
        raise HTTPException(status_code=500, detail='Failed to load user session')
    return {'user': UserRead.model_validate(fresh_user), 'csrf_token': csrf_token}


@router.get('/session', response_model=SessionResponse)
async def session(current_user: User | None = Depends(get_optional_user)) -> SessionResponse:
    if not current_user:
        return SessionResponse(authenticated=False, user=None)
    return SessionResponse(authenticated=True, user=UserRead.model_validate(current_user))


@router.post('/logout', response_model=MessageResponse)
async def logout(
    response: Response,
    _: None = Depends(require_csrf),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    clear_auth_cookies(response)
    return MessageResponse(message=f'Logged out {current_user.username}')


@router.get('/profile', response_model=UserRead)
async def profile(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.put('/profile', response_model=UserRead)
async def update_profile(
    payload: UserProfileUpdate,
    _: None = Depends(require_csrf),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    await db.commit()
    fresh_user = await _load_user_with_roles(db, current_user.id)
    if not fresh_user:
        raise HTTPException(status_code=500, detail='Failed to reload profile')
    return fresh_user


@router.post('/refresh')
async def refresh_token(response: Response, current_user: User = Depends(get_current_user)) -> dict:
    token = create_access_token(str(current_user.id))
    csrf_token = apply_auth_cookies(response, token)
    return {'csrf_token': csrf_token}


@router.put('/users/{user_id}/verification', response_model=UserRead)
async def update_verification(
    user_id: int,
    payload: VerificationUpdate,
    _: None = Depends(require_csrf),
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> User:
    result = await db.execute(select(User).options(selectinload(User.roles)).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    user.verification_status = payload.verification_status
    if payload.verification_status == 'approved':
        role_result = await db.execute(select(Role).where(Role.name == 'verified_member'))
        verified_role = role_result.scalar_one_or_none()
        if verified_role and not any(role.id == verified_role.id for role in user.roles):
            user.roles.append(verified_role)
    await db.commit()
    fresh_user = await _load_user_with_roles(db, user.id)
    if not fresh_user:
        raise HTTPException(status_code=500, detail='Failed to reload updated user')
    return fresh_user


@router.put('/users/{user_id}/roles', response_model=UserRead)
async def assign_roles(
    user_id: int,
    payload: RoleAssignment,
    _: None = Depends(require_csrf),
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> User:
    result = await db.execute(select(User).options(selectinload(User.roles)).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    roles_result = await db.execute(select(Role).where(Role.id.in_(payload.role_ids)))
    user.roles = list(roles_result.scalars().all())
    await db.commit()
    fresh_user = await _load_user_with_roles(db, user.id)
    if not fresh_user:
        raise HTTPException(status_code=500, detail='Failed to reload updated roles')
    return fresh_user
