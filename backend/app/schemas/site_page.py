from pydantic import BaseModel, Field

from app.schemas.common import TimestampedSchema


class SitePageUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
    is_published: bool = True


class SitePageRead(TimestampedSchema):
    id: int
    slug: str
    title: str
    content: str
    is_published: bool
