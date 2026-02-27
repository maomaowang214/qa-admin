"""
系统管理 - 用户 CRUD
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser, DbSession
from app.core.security import hash_password
from app.schemas.base import R
from app.schemas.user_system import UserSystemCreate, UserSystemOut, UserSystemUpdate

router = APIRouter(prefix="/system/user", tags=["system-user"])

SUPER_ADMIN_ROLE_NAME = "超级管理员"


async def _is_super_admin(db: AsyncSession, user_id: str) -> bool:
    from app.models.user import UserRole
    from app.models.role import Role

    r = await db.execute(
        select(Role)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == user_id, Role.name == SUPER_ADMIN_ROLE_NAME)
    )
    return r.scalars().first() is not None


def _user_to_out(u, role_names: list[str] | None = None, role_ids: list[str] | None = None):
    return {
        "id": u.id,
        "username": u.username,
        "nickname": u.nickname,
        "avatar": u.avatar,
        "status": u.status,
        "roleNames": role_names or [],
        "roleIds": role_ids or [],
        "createTime": u.created_at.isoformat() if u.created_at else None,
    }


@router.get("/list", response_model=R[dict])
async def user_list(db: DbSession, current_user: CurrentUser, page: int = 1, pageSize: int = 20,
    username: str | None = None, nickname: str | None = None, status: int | None = None):
    from app.models.user import User, UserRole
    from app.models.role import Role
    from sqlalchemy import func

    q = select(User)
    count_q = select(func.count()).select_from(User)
    if username:
        q = q.where(User.username.contains(username))
        count_q = count_q.where(User.username.contains(username))
    if nickname:
        q = q.where(User.nickname.contains(nickname))
        count_q = count_q.where(User.nickname.contains(nickname))
    if status is not None:
        q = q.where(User.status == status)
        count_q = count_q.where(User.status == status)

    total = (await db.execute(count_q)).scalar() or 0
    q = q.offset((page - 1) * pageSize).limit(pageSize)
    result = await db.execute(q)
    users = result.scalars().all()

    items = []
    for u in users:
        roles_res = await db.execute(
            select(Role).join(UserRole, UserRole.role_id == Role.id).where(UserRole.user_id == u.id)
        )
        roles = roles_res.scalars().all()
        role_names = [r.name for r in roles]
        role_ids = [r.id for r in roles]
        items.append(_user_to_out(u, role_names, role_ids))

    return R.ok(data={"items": items, "total": total})


@router.get("/username-exists", response_model=R[bool])
async def username_exists(db: DbSession, current_user: CurrentUser, username: str, id: str | None = None):
    from app.models.user import User

    q = select(User).where(User.username == username)
    if id:
        q = q.where(User.id != id)
    result = await db.execute(q)
    exists = result.scalars().first() is not None
    return R.ok(data=exists)


@router.post("", response_model=R[UserSystemOut])
async def user_create(data: UserSystemCreate, db: DbSession, current_user: CurrentUser):
    from app.models.user import User, UserRole

    existing = await db.execute(select(User).where(User.username == data.username))
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Username already exists")

    u = User(
        username=data.username,
        password_hash=hash_password(data.password),
        nickname=data.nickname,
        status=data.status,
    )
    db.add(u)
    await db.flush()

    for rid in data.roleIds:
        db.add(UserRole(user_id=u.id, role_id=rid))
    await db.refresh(u)

    role_names = []
    if data.roleIds:
        from app.models.role import Role
        roles_res = await db.execute(select(Role).where(Role.id.in_(data.roleIds)))
        role_names = [r.name for r in roles_res.scalars().all()]

    return R.ok(UserSystemOut(**_user_to_out(u, role_names, data.roleIds)))


@router.put("/{user_id}", response_model=R[UserSystemOut])
async def user_update(user_id: str, data: UserSystemUpdate, db: DbSession, current_user: CurrentUser):
    from sqlalchemy import delete
    from app.models.user import User, UserRole
    from app.models.role import Role

    result = await db.execute(select(User).where(User.id == user_id))
    u = result.scalars().first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")

    if data.password is not None:
        u.password_hash = hash_password(data.password)
    if data.nickname is not None:
        u.nickname = data.nickname
    if data.status is not None:
        if data.status == 0:
            if await _is_super_admin(db, user_id):
                raise HTTPException(status_code=400, detail="超级管理员账号不可禁用")
        u.status = data.status

    if data.roleIds is not None:
        await db.execute(delete(UserRole).where(UserRole.user_id == user_id))
        for rid in data.roleIds:
            db.add(UserRole(user_id=user_id, role_id=rid))

    await db.flush()
    await db.refresh(u)

    roles_res = await db.execute(
        select(Role).join(UserRole, UserRole.role_id == Role.id).where(UserRole.user_id == user_id)
    )
    role_names = [r.name for r in roles_res.scalars().all()]

    return R.ok(UserSystemOut(**_user_to_out(u, role_names)))


@router.delete("/{user_id}")
async def user_delete(user_id: str, db: DbSession, current_user: CurrentUser):
    from sqlalchemy import delete
    from app.models.user import User, UserRole

    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    if await _is_super_admin(db, user_id):
        raise HTTPException(status_code=400, detail="超级管理员账号不可删除")

    result = await db.execute(select(User).where(User.id == user_id))
    u = result.scalars().first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")

    await db.execute(delete(UserRole).where(UserRole.user_id == user_id))
    await db.delete(u)
    return R.ok()
