from app.schemas.common import ORMModel


class RoleRead(ORMModel):
    id: int
    name: str
    display_name: str
    color: str | None = None
    priority: int
