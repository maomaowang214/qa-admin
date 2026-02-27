"""系统管理 - 用户 CRUD 专用 Schema"""
from pydantic import BaseModel


class UserSystemCreate(BaseModel):
    username: str
    password: str
    nickname: str | None = None
    status: int = 1
    roleIds: list[str] = []


class UserSystemUpdate(BaseModel):
    password: str | None = None
    nickname: str | None = None
    status: int | None = None
    roleIds: list[str] | None = None


class UserSystemOut(BaseModel):
    id: str
    username: str
    nickname: str | None = None
    avatar: str | None = None
    status: int
    roleNames: list[str] = []
    roleIds: list[str] = []
    createTime: str | None = None

    model_config = {"from_attributes": True}
