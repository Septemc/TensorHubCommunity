from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_db, require_admin, require_csrf
from app.models import Announcement, Category, Post, Role, SitePage, User
from app.schemas.announcement import AnnouncementCreate, AnnouncementRead, AnnouncementUpdate
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.schemas.post import PostRead
from app.schemas.site_page import SitePageRead, SitePageUpdate
from app.schemas.user import UserRead
from app.utils.markdown import sanitize_markdown


router = APIRouter()


@router.get("/users", response_model=list[UserRead])
async def list_users(_: User = Depends(require_admin), db: AsyncSession = Depends(get_db)) -> list[User]:
    result = await db.execute(select(User).options(selectinload(User.roles)).order_by(desc(User.created_at)))
    return list(result.scalars().all())


@router.get("/roles")
async def list_roles(_: User = Depends(require_admin), db: AsyncSession = Depends(get_db)) -> list[dict]:
    result = await db.execute(select(Role).order_by(desc(Role.priority)))
    return [
        {"id": role.id, "name": role.name, "display_name": role.display_name, "color": role.color, "priority": role.priority}
        for role in result.scalars().all()
    ]


@router.post("/categories", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: CategoryCreate,
    _: None = Depends(require_csrf),
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Category:
    category = Category(**payload.model_dump())
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


@router.put("/categories/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: int,
    payload: CategoryUpdate,
    _: None = Depends(require_csrf),
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Category:
    category = await db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    for field, value in payload.model_dump().items():
        setattr(category, field, value)
    await db.commit()
    await db.refresh(category)
    return category


@router.get("/posts", response_model=list[PostRead])
async def list_admin_posts(_: User = Depends(require_admin), db: AsyncSession = Depends(get_db)) -> list[Post]:
    result = await db.execute(select(Post).options(selectinload(Post.author).selectinload(User.roles)).order_by(desc(Post.created_at)))
    return list(result.scalars().all())


@router.put("/posts/{post_id}/top", response_model=PostRead)
async def toggle_post_top(
    post_id: int,
    _: None = Depends(require_csrf),
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Post:
    result = await db.execute(select(Post).options(selectinload(Post.author).selectinload(User.roles)).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.is_top = not post.is_top
    await db.commit()
    await db.refresh(post)
    return post


@router.put("/posts/{post_id}/essence", response_model=PostRead)
async def toggle_post_essence(
    post_id: int,
    _: None = Depends(require_csrf),
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Post:
    result = await db.execute(select(Post).options(selectinload(Post.author).selectinload(User.roles)).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.is_essence = not post.is_essence
    await db.commit()
    await db.refresh(post)
    return post


@router.post("/announcements", response_model=AnnouncementRead, status_code=status.HTTP_201_CREATED)
async def create_announcement(
    payload: AnnouncementCreate,
    _: None = Depends(require_csrf),
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Announcement:
    announcement = Announcement(
        title=payload.title,
        content=sanitize_markdown(payload.content),
        cover_image=payload.cover_image,
        is_published=payload.is_published,
        user_id=current_admin.id,
    )
    db.add(announcement)
    await db.commit()
    result = await db.execute(
        select(Announcement).options(selectinload(Announcement.author).selectinload(User.roles)).where(Announcement.id == announcement.id)
    )
    return result.scalar_one()


@router.get("/announcements", response_model=list[AnnouncementRead])
async def list_admin_announcements(_: User = Depends(require_admin), db: AsyncSession = Depends(get_db)) -> list[Announcement]:
    result = await db.execute(
        select(Announcement).options(selectinload(Announcement.author).selectinload(User.roles)).order_by(desc(Announcement.created_at))
    )
    return list(result.scalars().all())


@router.put("/announcements/{announcement_id}", response_model=AnnouncementRead)
async def update_announcement(
    announcement_id: int,
    payload: AnnouncementUpdate,
    _: None = Depends(require_csrf),
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Announcement:
    result = await db.execute(
        select(Announcement).options(selectinload(Announcement.author).selectinload(User.roles)).where(Announcement.id == announcement_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Announcement not found")
    updates = payload.model_dump(exclude_unset=True)
    if "content" in updates:
        updates["content"] = sanitize_markdown(updates["content"])
    for field, value in updates.items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


@router.get("/site/pages/{slug}", response_model=SitePageRead)
async def get_site_page(slug: str, _: User = Depends(require_admin), db: AsyncSession = Depends(get_db)) -> SitePage:
    result = await db.execute(select(SitePage).where(SitePage.slug == slug))
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(status_code=404, detail="Site page not found")
    return page


@router.put("/site/pages/{slug}", response_model=SitePageRead)
async def update_site_page(
    slug: str,
    payload: SitePageUpdate,
    _: None = Depends(require_csrf),
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> SitePage:
    result = await db.execute(select(SitePage).where(SitePage.slug == slug))
    page = result.scalar_one_or_none()
    if not page:
        page = SitePage(slug=slug, updated_by=current_admin.id, **payload.model_dump())
        db.add(page)
    else:
        for field, value in payload.model_dump().items():
            setattr(page, field, value)
        page.updated_by = current_admin.id
    await db.commit()
    await db.refresh(page)
    return page
