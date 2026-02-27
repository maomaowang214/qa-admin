"""
认证：登录、刷新、登出、权限码
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import CurrentUser, DbSession, OptionalUser
from app.core.online_session import set_online
from app.core.security import create_access_token, hash_password, verify_password
from app.schemas.auth import LoginIn, LoginOut, RefreshOut
from app.schemas.base import R

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=R[LoginOut])
async def login(data: LoginIn, db: DbSession):
    from sqlalchemy import select
    from app.models.user import User

    if not data.username or not data.password:
        raise HTTPException(status_code=400, detail="username and password required")
    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalars().first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if user.status != 1:
        raise HTTPException(status_code=403, detail="User disabled")
    token = create_access_token(user.username)
    await set_online(str(user.id), user.username, user.nickname)
    return R.ok(LoginOut(accessToken=token))


@router.post("/refresh", response_model=R[RefreshOut])
async def refresh(current_user: CurrentUser):
    token = create_access_token(current_user.username)
    return R.ok(RefreshOut(data=token))


@router.post("/logout")
async def logout(current_user: OptionalUser):
    from app.core.online_session import remove_online

    if current_user:
        await remove_online(str(current_user.id))
    return R.ok()


@router.get("/codes", response_model=R[list[str]])
async def get_codes(current_user: CurrentUser, db: DbSession):
    """返回当前用户权限码列表（菜单 auth_code），供前端按钮级权限"""
    from sqlalchemy import select
    from app.models.role import Role
    from app.models.user import UserRole
    from app.models.menu import Menu

    result = await db.execute(
        select(Role)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == current_user.id)
    )
    roles = result.scalars().all()
    menu_ids: set[str] = set()
    for r in roles:
        if r.permissions:
            menu_ids.update(r.permissions)
    if not menu_ids:
        return R.ok([])
    menu_result = await db.execute(select(Menu).where(Menu.id.in_(menu_ids)))
    menus = menu_result.scalars().all()
    codes = [m.auth_code for m in menus if m.auth_code]
    return R.ok(list(dict.fromkeys(codes)))
