"""
系统管理 - 角色 CRUD
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import CurrentUser, DbSession
from app.schemas.base import R
from app.schemas.role import RoleCreate, RoleOut, RoleUpdate

router = APIRouter(prefix="/system/role", tags=["system-role"])

def _role_to_out(r):
    return {
        "id": r.id,
        "name": r.name,
        "remark": r.remark,
        "status": r.status,
        "permissions": r.permissions or [],
        "createTime": r.created_at.isoformat() if r.created_at else None,
    }

@router.get("/list", response_model=R[dict])
async def role_list(db: DbSession, current_user: CurrentUser, page: int = 1, pageSize: int = 20, name: str | None = None, status: int | None = None):
    from sqlalchemy import select, func
    from app.models.role import Role
    q = select(Role)
    count_q = select(func.count()).select_from(Role)
    if name:
        q = q.where(Role.name.contains(name))
        count_q = count_q.where(Role.name.contains(name))
    if status is not None:
        q = q.where(Role.status == status)
        count_q = count_q.where(Role.status == status)
    total = (await db.execute(count_q)).scalar() or 0
    q = q.offset((page - 1) * pageSize).limit(pageSize)
    result = await db.execute(q)
    items = result.scalars().all()
    return R.ok(data={"items": [_role_to_out(r) for r in items], "total": total})

@router.post("", response_model=R[RoleOut])
async def role_create(data: RoleCreate, db: DbSession, current_user: CurrentUser):
    from app.models.role import Role
    r = Role(name=data.name, remark=data.remark, status=data.status, permissions=data.permissions)
    db.add(r)
    await db.flush()
    await db.refresh(r)
    return R.ok(RoleOut(**_role_to_out(r)))

@router.put("/{role_id}", response_model=R[RoleOut])
async def role_update(role_id: str, data: RoleUpdate, db: DbSession, current_user: CurrentUser):
    from sqlalchemy import select
    from app.models.role import Role
    result = await db.execute(select(Role).where(Role.id == role_id))
    r = result.scalars().first()
    if not r:
        raise HTTPException(status_code=404, detail="Role not found")
    if data.name is not None:
        r.name = data.name
    if data.remark is not None:
        r.remark = data.remark
    if data.status is not None:
        r.status = data.status
    if data.permissions is not None:
        r.permissions = data.permissions
    await db.flush()
    await db.refresh(r)
    return R.ok(RoleOut(**_role_to_out(r)))

@router.delete("/{role_id}")
async def role_delete(role_id: str, db: DbSession, current_user: CurrentUser):
    from sqlalchemy import delete, select
    from app.models.role import Role
    from app.models.user import UserRole
    result = await db.execute(select(Role).where(Role.id == role_id))
    r = result.scalars().first()
    if not r:
        raise HTTPException(status_code=404, detail="Role not found")
    await db.execute(delete(UserRole).where(UserRole.role_id == role_id))
    await db.delete(r)
    return R.ok()
