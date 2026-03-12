from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Like(Base, TimestampMixin):
    __tablename__ = "likes"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    target_type: Mapped[str] = mapped_column(String(20), primary_key=True)
    target_id: Mapped[int] = mapped_column(Integer, primary_key=True)
