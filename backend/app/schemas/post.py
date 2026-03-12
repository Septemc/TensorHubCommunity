from pydantic import BaseModel, Field

from app.schemas.common import TimestampedSchema
from app.schemas.user import PublicUserRead


class PostCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    content: str = Field(min_length=3)
    category_id: int
    post_type: str = "general"
    extra_data: dict | None = None


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=255)
    content: str | None = Field(default=None, min_length=3)
    category_id: int | None = None
    post_type: str | None = None
    extra_data: dict | None = None
    is_top: bool | None = None
    is_essence: bool | None = None
    status: int | None = None


class PostRead(TimestampedSchema):
    id: int
    title: str
    content: str
    user_id: int
    category_id: int
    post_type: str
    extra_data: dict | None = None
    views: int
    likes_count: int
    comments_count: int
    is_top: bool
    is_essence: bool
    status: int
    author: PublicUserRead

