from fastapi import APIRouter

from app.api.v1 import auth, user, menu_routes
from app.api.v1.system import role, menu, dept, online, message, user as system_user

api_router = APIRouter()

# 认证（登录可不带 Token）
api_router.include_router(auth.router)
# 以下需要登录
api_router.include_router(user.router)
api_router.include_router(menu_routes.router)
api_router.include_router(role.router)
api_router.include_router(menu.router)
api_router.include_router(dept.router)
api_router.include_router(system_user.router)
api_router.include_router(online.router)
api_router.include_router(message.router)
