from sqlalchemy import Boolean, ForeignKey, Index, Integer, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Post(Base, TimestampMixin):
    __tablename__ = "posts"
    __table_args__ = (
        Index("ix_posts_category_created", "category_id", "created_at"),
        Index("ix_posts_status_top", "status", "is_top"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False)
    post_type: Mapped[str] = mapped_column(String(20), default="general", nullable=False)
    extra_data: Mapped[dict | None] = mapped_column(JSONB)
    views: Mapped[int] = mapped_column(Integer, default=0)
    likes_count: Mapped[int] = mapped_column(Integer, default=0)
    comments_count: Mapped[int] = mapped_column(Integer, default=0)
    is_top: Mapped[bool] = mapped_column(Boolean, default=False)
    is_essence: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[int] = mapped_column(SmallInteger, default=1)

    author = relationship("User", back_populates="posts")
    category = relationship("Category", back_populates="posts")
    comments = relationship("Comment", back_populates="post")
