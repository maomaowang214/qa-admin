from typing import Any

from pydantic import BaseModel


class MenuMeta(BaseModel):
    title: str | None = None
    icon: str | None = None
    activeIcon: str | None = None
    activePath: str | None = None
    hideInMenu: bool | None = None
    hideInTab: bool | None = None
    hideInBreadcrumb: bool | None = None
    hideChildrenInMenu: bool | None = None
    keepAlive: bool | None = None
    affixTab: bool | None = None
    link: str | None = None
    iframeSrc: str | None = None
    badge: str | None = None
    badgeType: str | None = None
    badgeVariants: str | None = None
    order: int | None = None

    model_config = {"extra": "allow"}


class MenuCreate(BaseModel):
    name: str
    path: str = ""
    pid: str = "0"
    type: str = "menu"
    component: str | None = None
    redirect: str | None = None
    authCode: str | None = None
    status: int = 1
    meta: dict[str, Any] | None = None


class MenuUpdate(BaseModel):
    name: str | None = None
    path: str | None = None
    pid: str | None = None
    type: str | None = None
    component: str | None = None
    redirect: str | None = None
    authCode: str | None = None
    status: int | None = None
    meta: dict[str, Any] | None = None


class MenuOut(BaseModel):
    id: str
    name: str
    path: str
    pid: str
    type: str
    component: str | None
    redirect: str | None
    authCode: str | None
    status: int
    meta: dict | None
    children: list["MenuOut"] | None = None
    createTime: str | None = None

    model_config = {"from_attributes": True}
