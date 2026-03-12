from datetime import datetime

from sqlalchemy import DateTime, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.role import user_roles


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(100), unique=True, index=True)
    real_name: Mapped[str] = mapped_column(String(50), nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    major: Mapped[str] = mapped_column(String(100), nullable=False)
    student_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    avatar: Mapped[str | None] = mapped_column(String(255))
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[int] = mapped_column(SmallInteger, default=1)
    verification_status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False, index=True)

    roles = relationship("Role", secondary=user_roles, back_populates="users", lazy="selectin")
    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="author")

    def has_role(self, role_name: str) -> bool:
        return any(role.name == role_name for role in self.roles)

    def has_any_role(self, role_names: set[str]) -> bool:
        return any(role.name in role_names for role in self.roles)

    @property
    def primary_role(self):
        return max(self.roles, key=lambda item: item.priority, default=None)
