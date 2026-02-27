"""
角色表
"""
from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Role(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "sys_role"

    name: Mapped[str] = mapped_column(String(64), index=True)
    remark: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    status: Mapped[int] = mapped_column(default=1)  # 0 禁用 1 启用
    permissions: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)  # 菜单/权限 ID 列表

    users: Mapped[list["UserRole"]] = relationship("UserRole", back_populates="role", lazy="selectin")
