"""
在线用户会话管理（Redis）
登录时写入，登出/踢出时删除，列表时扫描
"""
import json
from datetime import UTC, datetime

from app.config import settings
from app.core import redis


ONLINE_KEY_PREFIX = "online:"
ONLINE_KEY_TTL = settings.jwt_expire_minutes * 60  # 秒


def _key(user_id: str) -> str:
    return f"{ONLINE_KEY_PREFIX}{user_id}"


async def set_online(user_id: str, username: str, nickname: str | None) -> bool:
    """登录时记录在线"""
    data = {
        "user_id": user_id,
        "username": username,
        "nickname": nickname or username,
        "login_time": datetime.now(UTC).isoformat(),
    }
    return await redis.set(_key(user_id), json.dumps(data, ensure_ascii=False), ex=ONLINE_KEY_TTL)


async def remove_online(user_id: str) -> bool:
    """登出或踢出时移除"""
    return await redis.delete(_key(user_id))


async def refresh_online(user_id: str) -> bool:
    """刷新 TTL（可选：每次请求时调用以延长在线状态）"""
    r = redis.get_redis()
    if r is None:
        return False
    try:
        key = _key(user_id)
        return await r.expire(key, ONLINE_KEY_TTL)
    except Exception:
        return False


async def list_online() -> list[dict]:
    """获取所有在线用户列表"""
    keys = await redis.keys_by_pattern(f"{ONLINE_KEY_PREFIX}*")
    result = []
    for key in keys:
        val = await redis.get(key)
        if val:
            try:
                result.append(json.loads(val))
            except json.JSONDecodeError:
                pass
    return result
