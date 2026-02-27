"""
系统管理 - 在线用户
"""
from fastapi import APIRouter, Depends, HTTPException

from app.core.deps import CurrentUser
from app.core.online_session import list_online, remove_online
from app.schemas.base import R

router = APIRouter(prefix="/system/online", tags=["system-online"])

@router.get("/list", response_model=R[dict])
async def online_list(current_user: CurrentUser):
    items = await list_online()
    return R.ok(data={"items": items, "total": len(items)})

@router.post("/kick/{user_id}")
async def online_kick(user_id: str, current_user: CurrentUser):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot kick yourself")
    await remove_online(user_id)
    return R.ok()
