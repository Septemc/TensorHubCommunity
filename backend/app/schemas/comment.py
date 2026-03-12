from pydantic import BaseModel, Field

from app.schemas.common import TimestampedSchema
from app.schemas.user import PublicUserRead


class CommentCreate(BaseModel):
    content: str = Field(min_length=1)
    parent_id: int | None = None


class CommentUpdate(BaseModel):
    content: str = Field(min_length=1)


class CommentRead(TimestampedSchema):
    id: int
    content: str
    user_id: int
    post_id: int
    parent_id: int | None = None
    likes_count: int
    author: PublicUserRead

