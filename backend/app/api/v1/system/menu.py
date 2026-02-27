"""
系统管理 - 菜单 CRUD、name-exists、path-exists
"""
from fastapi import APIRouter, Depends, HTTPException

from app.core.deps import CurrentUser, DbSession
from app.schemas.base import R
from app.schemas.menu import MenuCreate, MenuOut, MenuUpdate

router = APIRouter(prefix="/system/menu", tags=["system-menu"])


def _menu_to_out(m, children=None):
    d = {
        "id": m.id,
        "name": m.name,
        "path": m.path or "",
        "pid": m.pid or "0",
        "type": m.type,
        "component": m.component,
        "redirect": m.redirect,
        "authCode": m.auth_code or "",
        "status": m.status,
        "meta": m.meta or {},
        "createTime": m.created_at.isoformat() if m.created_at else None,
    }
    if children is not None:
        d["children"] = children
    return d


def _build_menu_tree(menus, pid="0"):
    out = []
    for m in menus:
        if (m.pid or "0") == pid:
            children = _build_menu_tree(menus, m.id)
            out.append(_menu_to_out(m, children))
    return out


@router.get("/list", response_model=R[list])
async def menu_list(db: DbSession, current_user: CurrentUser):
    from sqlalchemy import select
    from app.models.menu import Menu

    result = await db.execute(select(Menu).order_by(Menu.id))
    all_menus = result.scalars().all()
    tree = _build_menu_tree(all_menus)
    return R.ok(tree)


@router.get("/name-exists", response_model=R[bool])
async def menu_name_exists(db: DbSession, current_user: CurrentUser, name: str, id: str | None = None):
    from sqlalchemy import select
    from app.models.menu import Menu

    q = select(Menu).where(Menu.name == name)
    if id:
        q = q.where(Menu.id != id)
    result = await db.execute(q)
    exists = result.scalars().first() is not None
    return R.ok(exists)


@router.get("/path-exists", response_model=R[bool])
async def menu_path_exists(db: DbSession, current_user: CurrentUser, path: str, id: str | None = None):
    from sqlalchemy import select
    from app.models.menu import Menu

    q = select(Menu).where(Menu.path == path)
    if id:
        q = q.where(Menu.id != id)
    result = await db.execute(q)
    exists = result.scalars().first() is not None
    return R.ok(exists)


@router.post("", response_model=R[dict])
async def menu_create(data: MenuCreate, db: DbSession, current_user: CurrentUser):
    from app.models.menu import Menu

    m = Menu(
        name=data.name,
        path=data.path,
        pid=data.pid,
        type=data.type,
        component=data.component,
        redirect=data.redirect,
        auth_code=data.authCode,
        status=data.status,
        meta=data.meta,
    )
    db.add(m)
    await db.flush()
    await db.refresh(m)
    return R.ok(_menu_to_out(m))


@router.put("/{menu_id}", response_model=R[dict])
async def menu_update(menu_id: str, data: MenuUpdate, db: DbSession, current_user: CurrentUser):
    from sqlalchemy import select
    from app.models.menu import Menu

    result = await db.execute(select(Menu).where(Menu.id == menu_id))
    m = result.scalars().first()
    if not m:
        raise HTTPException(status_code=404, detail="Menu not found")
    if data.name is not None:
        m.name = data.name
    if data.path is not None:
        m.path = data.path
    if data.pid is not None:
        m.pid = data.pid
    if data.type is not None:
        m.type = data.type
    if data.component is not None:
        m.component = data.component
    if data.redirect is not None:
        m.redirect = data.redirect
    if data.authCode is not None:
        m.auth_code = data.authCode
    if data.status is not None:
        m.status = data.status
    if data.meta is not None:
        m.meta = data.meta
    await db.flush()
    await db.refresh(m)
    return R.ok(_menu_to_out(m))


@router.delete("/{menu_id}")
async def menu_delete(menu_id: str, db: DbSession, current_user: CurrentUser):
    from sqlalchemy import select
    from app.models.menu import Menu

    result = await db.execute(select(Menu).where(Menu.id == menu_id))
    m = result.scalars().first()
    if not m:
        raise HTTPException(status_code=404, detail="Menu not found")
    child = await db.execute(select(Menu).where(Menu.pid == menu_id))
    if child.scalars().first():
        raise HTTPException(status_code=400, detail="Has children, delete children first")
    await db.delete(m)
    return R.ok()
