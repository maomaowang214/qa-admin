#!/usr/bin/env python3
"""
统一响应格式：与前端 @vben/request 约定一致
"""
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class R(BaseModel, Generic[T]):
    code: int = 0
    data: T | None = None
    message: str | None = None

    @classmethod
    def ok(cls, data: T | None = None, message: str | None = None) -> "R[T]":
        return cls(code=0, data=data, message=message)

    @classmethod
    def fail(cls, code: int = -1, message: str = "error", data: T | None = None) -> "R[T]":
        return cls(code=code, data=data, message=message)
