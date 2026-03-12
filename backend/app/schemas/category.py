from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = None
    parent_id: int | None = None
    type: str = "forum"
    sort_order: int = 0
    is_active: bool = True


class CategoryUpdate(CategoryCreate):
    pass


class CategoryRead(ORMModel):
    id: int
    name: str
    description: str | None = None
    parent_id: int | None = None
    type: str
    sort_order: int
    is_active: bool
