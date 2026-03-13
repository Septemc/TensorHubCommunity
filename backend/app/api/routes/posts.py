from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_current_user, get_db, require_csrf, require_verified_user
from app.models import Category, Comment, Like, Post, User
from app.schemas.comment import CommentCreate, CommentRead
from app.schemas.post import PostCreate, PostRead, PostUpdate
from app.utils.markdown import sanitize_markdown

router = APIRouter()


async def _load_post(post_id: int, db: AsyncSession) -> Post | None:
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.author).selectinload(User.roles), selectinload(Post.comments))
        .where(Post.id == post_id)
    )
    return result.scalar_one_or_none()


@router.post('', response_model=PostRead, status_code=status.HTTP_201_CREATED)
async def create_post(
    payload: PostCreate,
    _: None = Depends(require_csrf),
    current_user: User = Depends(require_verified_user),
    db: AsyncSession = Depends(get_db),
) -> Post:
    category_result = await db.execute(select(Category).where(Category.id == payload.category_id, Category.is_active.is_(True)))
    category = category_result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail='Category not found')
    if category.type == 'notice' and not current_user.has_role('admin'):
        raise HTTPException(status_code=403, detail='Only admins can post in notice category')

    post_data = payload.model_dump()
    post_data['content'] = sanitize_markdown(payload.content)
    post_data['user_id'] = current_user.id
    post = Post(**post_data)
    db.add(post)
    await db.commit()
    loaded = await _load_post(post.id, db)
    if not loaded:
        raise HTTPException(status_code=500, detail='Failed to load created post')
    return loaded


@router.get('', response_model=list[PostRead])
async def list_posts(sort: str = 'latest', db: AsyncSession = Depends(get_db)) -> list[Post]:
    stmt = select(Post).options(selectinload(Post.author).selectinload(User.roles)).where(Post.status == 1)
    if sort == 'hot':
        stmt = stmt.order_by(desc(Post.is_top), desc(Post.likes_count), desc(Post.comments_count), desc(Post.created_at))
    else:
        stmt = stmt.order_by(desc(Post.is_top), desc(Post.created_at))
    result = await db.execute(stmt.limit(30))
    return list(result.scalars().all())


@router.get('/{post_id}', response_model=PostRead)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)) -> Post:
    post = await _load_post(post_id, db)
    if not post or post.status == -1:
        raise HTTPException(status_code=404, detail='Post not found')
    post.views += 1
    await db.commit()
    await db.refresh(post)
    return post


@router.put('/{post_id}', response_model=PostRead)
async def update_post(
    post_id: int,
    payload: PostUpdate,
    _: None = Depends(require_csrf),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Post:
    post = await _load_post(post_id, db)
    if not post:
        raise HTTPException(status_code=404, detail='Post not found')
    if post.user_id != current_user.id and not current_user.has_any_role({'admin', 'super_moderator', 'moderator'}):
        raise HTTPException(status_code=403, detail='No permission')
    updates = payload.model_dump(exclude_unset=True)
    if 'content' in updates:
        updates['content'] = sanitize_markdown(updates['content'])
    for field, value in updates.items():
        setattr(post, field, value)
    await db.commit()
    await db.refresh(post)
    reloaded = await _load_post(post_id, db)
    if not reloaded:
        raise HTTPException(status_code=500, detail='Failed to reload updated post')
    return reloaded


@router.delete('/{post_id}')
async def delete_post(
    post_id: int,
    _: None = Depends(require_csrf),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    post = await _load_post(post_id, db)
    if not post:
        raise HTTPException(status_code=404, detail='Post not found')
    if post.user_id != current_user.id and not current_user.has_any_role({'admin', 'super_moderator', 'moderator'}):
        raise HTTPException(status_code=403, detail='No permission')
    post.status = -1
    await db.commit()
    return {'message': 'Post deleted'}


@router.post('/{post_id}/like')
async def toggle_post_like(
    post_id: int,
    _: None = Depends(require_csrf),
    current_user: User = Depends(require_verified_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    post = await db.get(Post, post_id)
    if not post or post.status != 1:
        raise HTTPException(status_code=404, detail='Post not found')
    like = await db.get(Like, {'user_id': current_user.id, 'target_type': 'post', 'target_id': post_id})
    liked = False
    if like:
        await db.delete(like)
        post.likes_count = max(0, post.likes_count - 1)
    else:
        db.add(Like(user_id=current_user.id, target_type='post', target_id=post_id))
        post.likes_count += 1
        liked = True
    await db.commit()
    return {'liked': liked, 'likes_count': post.likes_count}


@router.get('/{post_id}/comments', response_model=list[CommentRead])
async def list_post_comments(post_id: int, db: AsyncSession = Depends(get_db)) -> list[Comment]:
    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.author).selectinload(User.roles))
        .where(Comment.post_id == post_id)
        .order_by(Comment.created_at)
    )
    return list(result.scalars().all())


@router.post('/{post_id}/comments', response_model=CommentRead, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: int,
    payload: CommentCreate,
    _: None = Depends(require_csrf),
    current_user: User = Depends(require_verified_user),
    db: AsyncSession = Depends(get_db),
) -> Comment:
    post = await db.get(Post, post_id)
    if not post or post.status != 1:
        raise HTTPException(status_code=404, detail='Post not found')
    if payload.parent_id:
        parent = await db.get(Comment, payload.parent_id)
        if not parent or parent.post_id != post_id:
            raise HTTPException(status_code=400, detail='Invalid parent comment')
    comment = Comment(content=sanitize_markdown(payload.content), user_id=current_user.id, post_id=post_id, parent_id=payload.parent_id)
    db.add(comment)
    post.comments_count += 1
    await db.commit()
    result = await db.execute(
        select(Comment).options(selectinload(Comment.author).selectinload(User.roles)).where(Comment.id == comment.id)
    )
    return result.scalar_one()


