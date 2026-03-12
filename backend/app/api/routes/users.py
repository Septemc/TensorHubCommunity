from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_db
from app.models import Post, User
from app.schemas.post import PostRead
from app.schemas.user import PublicUserRead


router = APIRouter()


@router.get("/{user_id}", response_model=PublicUserRead)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)) -> User:
    result = await db.execute(select(User).options(selectinload(User.roles)).where(User.id == user_id, User.status == 1))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{user_id}/posts", response_model=list[PostRead])
async def get_user_posts(user_id: int, db: AsyncSession = Depends(get_db)) -> list[Post]:
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.author).selectinload(User.roles))
        .where(Post.user_id == user_id, Post.status == 1)
        .order_by(desc(Post.created_at))
    )
    return list(result.scalars().all())
