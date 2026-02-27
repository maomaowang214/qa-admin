"""
站内消息表
"""
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Message(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "sys_message"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("sys_user.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(Text)
    avatar: Mapped[str | None] = mapped_column(String(512), nullable=True, default=None)
    link: Mapped[str | None] = mapped_column(String(512), nullable=True, default=None)
    is_read: Mapped[int] = mapped_column(default=0)  # 0 未读 1 已读
