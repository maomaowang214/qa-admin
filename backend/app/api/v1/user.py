"""
用户信息（需登录）
"""
from fastapi import APIRouter

from app.core.deps import CurrentUser, DbSession
from app.schemas.base import R
from app.schemas.user import UserInfoOut

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/info", response_model=R[UserInfoOut])
async def get_user_info(current_user: CurrentUser, db: DbSession):
    from sqlalchemy import select
    from app.models.role import Role
    from app.models.user import UserRole

    roles_result = await db.execute(
        select(Role)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == current_user.id)
    )
    roles = roles_result.scalars().all()
    role_names = [r.name for r in roles]
    permissions: list[str] = []
    for r in roles:
        if r.permissions:
            permissions.extend(r.permissions)
    return R.ok(
        UserInfoOut(
            userId=current_user.id,
            username=current_user.username,
            nickname=current_user.nickname,
            avatar=current_user.avatar,
            roles=role_names,
            permissions=list(dict.fromkeys(permissions)),
        )
    )
