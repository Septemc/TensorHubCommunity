from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_db
from app.models import Announcement, Post, SitePage, User
from app.schemas.announcement import AnnouncementRead
from app.schemas.post import PostRead
from app.schemas.site_page import SitePageRead


router = APIRouter()


@router.get("/home")
async def home(db: AsyncSession = Depends(get_db)) -> dict:
    page_result = await db.execute(select(SitePage).where(SitePage.slug == "home", SitePage.is_published.is_(True)))
    announcements_result = await db.execute(
        select(Announcement)
        .options(selectinload(Announcement.author).selectinload(User.roles))
        .where(Announcement.is_published.is_(True))
        .order_by(desc(Announcement.created_at))
        .limit(5)
    )
    posts_result = await db.execute(
        select(Post)
        .options(selectinload(Post.author).selectinload(User.roles))
        .where(Post.status == 1)
        .order_by(desc(Post.is_top), desc(Post.likes_count), desc(Post.created_at))
        .limit(6)
    )
    categories_count = await db.scalar(select(func.count()).select_from(Post))
    page = page_result.scalar_one_or_none()
    return {
        "page": SitePageRead.model_validate(page) if page else None,
        "announcements": [AnnouncementRead.model_validate(item) for item in announcements_result.scalars().all()],
        "hot_posts": [PostRead.model_validate(item) for item in posts_result.scalars().all()],
        "stats": {"posts": categories_count or 0},
    }


@router.get("/pages/{slug}", response_model=SitePageRead)
async def get_page(slug: str, db: AsyncSession = Depends(get_db)) -> SitePage:
    result = await db.execute(select(SitePage).where(SitePage.slug == slug, SitePage.is_published.is_(True)))
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page


@router.get("/announcements", response_model=list[AnnouncementRead])
async def list_announcements(db: AsyncSession = Depends(get_db)) -> list[Announcement]:
    result = await db.execute(
        select(Announcement)
        .options(selectinload(Announcement.author).selectinload(User.roles))
        .where(Announcement.is_published.is_(True))
        .order_by(desc(Announcement.created_at))
    )
    return list(result.scalars().all())


@router.get("/announcements/{announcement_id}", response_model=AnnouncementRead)
async def get_announcement(announcement_id: int, db: AsyncSession = Depends(get_db)) -> Announcement:
    result = await db.execute(
        select(Announcement)
        .options(selectinload(Announcement.author).selectinload(User.roles))
        .where(Announcement.id == announcement_id, Announcement.is_published.is_(True))
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return item
