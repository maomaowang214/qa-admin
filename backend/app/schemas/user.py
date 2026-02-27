from pydantic import BaseModel


class UserInfoOut(BaseModel):
    userId: str
    username: str
    nickname: str | None = None
    avatar: str | None = None
    roles: list[str] = []
    permissions: list[str] = []

    model_config = {"from_attributes": True}
