"""
菜单表：树形结构，支持目录/菜单/按钮/外链/内嵌
"""
from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Menu(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "sys_menu"

    name: Mapped[str] = mapped_column(String(64), index=True)
    path: Mapped[str] = mapped_column(String(255), default="")
    pid: Mapped[str] = mapped_column(String(36), ForeignKey("sys_menu.id"), default="0", index=True)  # 父级 ID，0 为根
    type: Mapped[str] = mapped_column(String(20), default="menu")  # catalog | menu | embedded | link | button
    component: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    redirect: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    auth_code: Mapped[str | None] = mapped_column(String(64), nullable=True, default=None)
    status: Mapped[int] = mapped_column(default=1)  # 0 禁用 1 启用
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=dict)  # 前端 meta 配置

    children: Mapped[list["Menu"]] = relationship(
        "Menu",
        back_populates="parent",
        lazy="selectin",
    )
    parent: Mapped["Menu | None"] = relationship(
        "Menu",
        back_populates="children",
        remote_side="Menu.id",
    )
