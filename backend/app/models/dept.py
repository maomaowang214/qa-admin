"""
部门表：树形结构
"""
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Dept(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "sys_dept"

    name: Mapped[str] = mapped_column(String(64), index=True)
    pid: Mapped[str] = mapped_column(String(36), ForeignKey("sys_dept.id"), default="0", index=True)  # 父级 ID，0 为根
    remark: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    status: Mapped[int] = mapped_column(default=1)  # 0 禁用 1 启用

    children: Mapped[list["Dept"]] = relationship(
        "Dept",
        back_populates="parent",
        lazy="selectin",
    )
    parent: Mapped["Dept | None"] = relationship(
        "Dept",
        back_populates="children",
        remote_side="Dept.id",
    )
