from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_current_user, get_db, require_csrf, require_verified_user
from app.models import Comment, Like, User
from app.schemas.comment import CommentRead, CommentUpdate
from app.utils.markdown import sanitize_markdown


router = APIRouter()


async def _load_comment(comment_id: int, db: AsyncSession) -> Comment | None:
    result = await db.execute(
        select(Comment).options(selectinload(Comment.author).selectinload(User.roles)).where(Comment.id == comment_id)
    )
    return result.scalar_one_or_none()


@router.get("/{comment_id}", response_model=CommentRead)
async def get_comment(comment_id: int, db: AsyncSession = Depends(get_db)) -> Comment:
    comment = await _load_comment(comment_id, db)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


@router.put("/{comment_id}", response_model=CommentRead)
async def update_comment(
    comment_id: int,
    payload: CommentUpdate,
    _: None = Depends(require_csrf),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Comment:
    comment = await _load_comment(comment_id, db)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != current_user.id and not current_user.has_any_role({"admin", "super_moderator", "moderator"}):
        raise HTTPException(status_code=403, detail="No permission")
    comment.content = sanitize_markdown(payload.content)
    await db.commit()
    await db.refresh(comment)
    return await _load_comment(comment_id, db)


@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: int,
    _: None = Depends(require_csrf),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    comment = await db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != current_user.id and not current_user.has_any_role({"admin", "super_moderator", "moderator"}):
        raise HTTPException(status_code=403, detail="No permission")
    await db.delete(comment)
    await db.commit()
    return {"message": "Comment deleted"}


@router.post("/{comment_id}/like")
async def toggle_comment_like(
    comment_id: int,
    _: None = Depends(require_csrf),
    current_user: User = Depends(require_verified_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    comment = await db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    like = await db.get(Like, {"user_id": current_user.id, "target_type": "comment", "target_id": comment_id})
    liked = False
    if like:
        await db.delete(like)
        comment.likes_count = max(0, comment.likes_count - 1)
    else:
        db.add(Like(user_id=current_user.id, target_type="comment", target_id=comment_id))
        comment.likes_count += 1
        liked = True
    await db.commit()
    return {"liked": liked, "likes_count": comment.likes_count}
