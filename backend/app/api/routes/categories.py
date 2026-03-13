from fastapi import APIRouter, Depends
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_db
from app.models import Category, Post, User
from app.schemas.category import CategoryRead
from app.schemas.post import PostRead


router = APIRouter()


@router.get("", response_model=list[CategoryRead])
async def list_categories(db: AsyncSession = Depends(get_db)) -> list[dict]:
    result = await db.execute(
        select(
            Category,
            func.count(Post.id).label("posts_count"),
        )
        .outerjoin(Post, (Post.category_id == Category.id) & (Post.status == 1))
        .where(Category.is_active.is_(True))
        .group_by(Category.id)
        .order_by(Category.sort_order, Category.id)
    )
    rows = result.all()
    return [
        {
            **CategoryRead.model_validate(category).model_dump(),
            "posts_count": posts_count,
        }
        for category, posts_count in rows
    ]


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