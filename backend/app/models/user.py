"""
用户表：登录、权限关联
"""
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "sys_user"

    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    nickname: Mapped[str | None] = mapped_column(String(64), nullable=True, default=None)
    avatar: Mapped[str | None] = mapped_column(String(512), nullable=True, default=None)
    status: Mapped[int] = mapped_column(default=1)  # 0 禁用 1 启用

    roles: Mapped[list["UserRole"]] = relationship("UserRole", back_populates="user", lazy="selectin")


class UserRole(Base):
    __tablename__ = "sys_user_role"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("sys_user.id"), primary_key=True)
    role_id: Mapped[str] = mapped_column(String(36), ForeignKey("sys_role.id"), primary_key=True)

    user: Mapped["User"] = relationship("User", back_populates="roles")
    role: Mapped["Role"] = relationship("Role", back_populates="users")
