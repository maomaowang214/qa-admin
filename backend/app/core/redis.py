"""
Redis 可选缓存（未配置或连接失败时降级为无缓存）
"""
from typing import Any

from app.config import settings

_redis_client: Any = None


def get_redis():
    global _redis_client
    if _redis_client is None:
        try:
            import redis.asyncio as aioredis
            _redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
        except Exception:
            _redis_client = None
    return _redis_client


async def keys_by_pattern(pattern: str) -> list[str]:
    """扫描匹配 pattern 的 key 列表（生产环境用 SCAN 替代 KEYS）"""
    r = get_redis()
    if r is None:
        return []
    try:
        return [k async for k in r.scan_iter(match=pattern, count=100)]
    except Exception:
        return []


async def get(key: str) -> str | None:
    r = get_redis()
    if r is None:
        return None
    try:
        return await r.get(key)
    except Exception:
        return None


async def set(key: str, value: str, ex: int | None = None) -> bool:
    r = get_redis()
    if r is None:
        return False
    try:
        await r.set(key, value, ex=ex)
        return True
    except Exception:
        return False


async def delete(key: str) -> bool:
    r = get_redis()
    if r is None:
        return False
    try:
        await r.delete(key)
        return True
    except Exception:
        return False
