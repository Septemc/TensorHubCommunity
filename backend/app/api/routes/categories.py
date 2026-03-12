from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_db
from app.models import Category, Post, User
from app.schemas.category import CategoryRead
from app.schemas.post import PostRead


router = APIRouter()


@router.get("", response_model=list[CategoryRead])
async def list_categories(db: AsyncSession = Depends(get_db)) -> list[Category]:
    result = await db.execute(select(Category).where(Category.is_active.is_(True)).order_by(Category.sort_order, Category.id))
    return list(result.scalars().all())


@router.get("/{category_id}/posts", response_model=list[PostRead])
async def list_category_posts(category_id: int, sort: str = "latest", db: AsyncSession = Depends(get_db)) -> list[Post]:
    stmt = (
        select(Post)
        .options(selectinload(Post.author).selectinload(User.roles))
        .where(Post.category_id == category_id, Post.status == 1)
    )
    if sort == "hot":
        stmt = stmt.order_by(desc(Post.is_top), desc(Post.likes_count), desc(Post.comments_count), desc(Post.created_at))
    else:
        stmt = stmt.order_by(desc(Post.is_top), desc(Post.created_at))
    result = await db.execute(stmt)
    return list(result.scalars().all())
