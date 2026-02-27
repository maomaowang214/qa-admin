from pydantic import BaseModel


class RoleCreate(BaseModel):
    name: str
    remark: str | None = None
    status: int = 1
    permissions: list[str] = []


class RoleUpdate(BaseModel):
    name: str | None = None
    remark: str | None = None
    status: int | None = None
    permissions: list[str] | None = None


class RoleOut(BaseModel):
    id: str
    name: str
    remark: str | None
    status: int
    permissions: list
    createTime: str | None = None

    model_config = {"from_attributes": True}
