"""
侧栏菜单（树形，需登录）
"""
from fastapi import APIRouter

from app.core.deps import CurrentUser, DbSession
from app.schemas.base import R

router = APIRouter(prefix="/menu", tags=["menu"])


@router.get("/all", response_model=R[list])
async def get_all_menus(current_user: CurrentUser, db: DbSession):
    """返回前端路由所需菜单树（根据用户角色过滤）"""
    from sqlalchemy import select
    from app.models.menu import Menu
    from app.models.role import Role
    from app.models.user import UserRole

    # 当前用户角色拥有的菜单/权限 ID
    role_result = await db.execute(
        select(Role)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == current_user.id)
    )
    roles = role_result.scalars().all()
    allowed_ids: set[str] = set()
    for r in roles:
        if r.permissions:
            allowed_ids.update(r.permissions)

    result = await db.execute(select(Menu).where(Menu.status == 1).order_by(Menu.id))
    all_menus = result.scalars().all()

    def menu_to_route(m: Menu) -> dict | None:
        if allowed_ids and m.id not in allowed_ids and m.type != "catalog":
            return None
        meta = m.meta or {}
        route: dict = {
            "id": m.id,
            "name": m.name,
            "path": m.path or "/",
            "component": m.component,
            "redirect": m.redirect,
            "meta": {
                "title": meta.get("title") or m.name,
                "icon": meta.get("icon"),
                "order": meta.get("order"),
                "hideInMenu": meta.get("hideInMenu"),
                "hideInTab": meta.get("hideInTab"),
                "keepAlive": meta.get("keepAlive"),
                "affixTab": meta.get("affixTab"),
            },
        }
        children = [menu_to_route(c) for c in (m.children or [])]
        route["children"] = [c for c in children if c]
        if route["children"] or m.type == "catalog":
            return route
        if m.type in ("menu", "link", "embedded", "button"):
            return route
        return route

    tree: list[dict] = []
    by_pid: dict[str, list[Menu]] = {}
    for m in all_menus:
        pid = m.pid or "0"
        by_pid.setdefault(pid, []).append(m)
    for m in all_menus:
        m.children = by_pid.get(m.id) or []
    roots = by_pid.get("0", [])
    for r in roots:
        item = menu_to_route(r)
        if item:
            tree.append(item)
    return R.ok(tree)
