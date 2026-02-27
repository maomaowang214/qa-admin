"""
系统管理 - 部门 CRUD
"""
from fastapi import APIRouter, Depends, HTTPException

from app.core.deps import CurrentUser, DbSession
from app.schemas.base import R
from app.schemas.dept import DeptCreate, DeptOut, DeptUpdate

router = APIRouter(prefix="/system/dept", tags=["system-dept"])


def _dept_to_out(d, children=None):
    out = {
        "id": d.id,
        "name": d.name,
        "pid": d.pid or "0",
        "remark": d.remark,
        "status": d.status,
        "createTime": d.created_at.isoformat() if d.created_at else None,
    }
    if children is not None:
        out["children"] = children
    return out


def _build_dept_tree(depts, pid="0"):
    result = []
    for d in depts:
        if (d.pid or "0") == pid:
            children = _build_dept_tree(depts, d.id)
            result.append(_dept_to_out(d, children))
    return result


@router.get("/list", response_model=R[list])
async def dept_list(db: DbSession, current_user: CurrentUser):
    from sqlalchemy import select
    from app.models.dept import Dept

    result = await db.execute(select(Dept).order_by(Dept.id))
    all_depts = result.scalars().all()
    tree = _build_dept_tree(all_depts)
    return R.ok(tree)


@router.post("", response_model=R[dict])
async def dept_create(data: DeptCreate, db: DbSession, current_user: CurrentUser):
    from app.models.dept import Dept

    d = Dept(name=data.name, pid=data.pid or "0", remark=data.remark, status=data.status)
    db.add(d)
    await db.flush()
    await db.refresh(d)
    return R.ok(_dept_to_out(d))


@router.put("/{dept_id}", response_model=R[dict])
async def dept_update(dept_id: str, data: DeptUpdate, db: DbSession, current_user: CurrentUser):
    from sqlalchemy import select
    from app.models.dept import Dept

    result = await db.execute(select(Dept).where(Dept.id == dept_id))
    d = result.scalars().first()
    if not d:
        raise HTTPException(status_code=404, detail="Dept not found")
    if data.name is not None:
        d.name = data.name
    if data.pid is not None:
        d.pid = data.pid
    if data.remark is not None:
        d.remark = data.remark
    if data.status is not None:
        d.status = data.status
    await db.flush()
    await db.refresh(d)
    return R.ok(_dept_to_out(d))


@router.delete("/{dept_id}")
async def dept_delete(dept_id: str, db: DbSession, current_user: CurrentUser):
    from sqlalchemy import select
    from app.models.dept import Dept

    result = await db.execute(select(Dept).where(Dept.id == dept_id))
    d = result.scalars().first()
    if not d:
        raise HTTPException(status_code=404, detail="Dept not found")
    child = await db.execute(select(Dept).where(Dept.pid == dept_id))
    if child.scalars().first():
        raise HTTPException(status_code=400, detail="Has children, delete children first")
    await db.delete(d)
    return R.ok()
