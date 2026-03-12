from pydantic import BaseModel, Field

from app.schemas.common import TimestampedSchema
from app.schemas.user import PublicUserRead


class AnnouncementCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    content: str = Field(min_length=3)
    cover_image: str | None = Field(default=None, max_length=255)
    is_published: bool = True


class AnnouncementUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=255)
    content: str | None = Field(default=None, min_length=3)
    cover_image: str | None = Field(default=None, max_length=255)
    is_published: bool | None = None


class AnnouncementRead(TimestampedSchema):
    id: int
    title: str
    content: str
    cover_image: str | None = None
    is_published: bool
    author: PublicUserRead | None = None

