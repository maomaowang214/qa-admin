from pydantic import BaseModel


class LoginIn(BaseModel):
    username: str | None = None
    password: str | None = None


class LoginOut(BaseModel):
    accessToken: str


class RefreshOut(BaseModel):
    data: str
    status: int = 200
