from pydantic import BaseModel


class DeptCreate(BaseModel):
    name: str
    pid: str | None = "0"
    remark: str | None = None
    status: int = 1


class DeptUpdate(BaseModel):
    name: str | None = None
    pid: str | None = None
    remark: str | None = None
    status: int | None = None


class DeptOut(BaseModel):
    id: str
    name: str
    pid: str | None
    remark: str | None
    status: int
    children: list["DeptOut"] | None = None
    createTime: str | None = None

    model_config = {"from_attributes": True}
