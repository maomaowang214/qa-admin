"""
系统管理 - 站内消息
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.core.deps import CurrentUser, DbSession
from app.models.message import Message
from app.schemas.base import R

router = APIRouter(prefix="/system/message", tags=["system-message"])

SUPER_ADMIN_ROLE_NAME = "超级管理员"


async def _is_super_admin(db, user_id: str) -> bool:
    from sqlalchemy import select
    from app.models.role import Role
    from app.models.user import UserRole

    r = await db.execute(
        select(Role)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == user_id, Role.name == SUPER_ADMIN_ROLE_NAME)
    )
    return r.scalars().first() is not None


def _to_notification_item(m: Message, *, receiver_username: str | None = None) -> dict:
    dt = m.created_at
    date_str = dt.strftime("%Y-%m-%d %H:%M:%S") if dt else ""
    data: dict = {
        "id": m.id,
        "avatar": m.avatar or "",
        "date": date_str,
        "isRead": m.is_read == 1,
        "message": m.message,
        "title": m.title,
        "link": m.link,
        "userId": m.user_id,
    }
    if receiver_username:
        data["receiverName"] = receiver_username
    return data


@router.get("/list", response_model=R[dict])
async def message_list(db: DbSession, current_user: CurrentUser, page: int = 1, pageSize: int = 20,
    title: str | None = None, isRead: int | None = None, userId: str | None = None):
    from sqlalchemy import select, func
    from app.models.user import User

    is_super = await _is_super_admin(db, current_user.id)

    if is_super:
        q = select(Message)
        count_q = select(func.count()).select_from(Message)
        if userId:
            q = q.where(Message.user_id == userId)
            count_q = count_q.where(Message.user_id == userId)
    else:
        q = select(Message).where(Message.user_id == current_user.id)
        count_q = select(func.count()).select_from(Message).where(Message.user_id == current_user.id)

    if title:
        q = q.where(Message.title.contains(title))
        count_q = count_q.where(Message.title.contains(title))
    if isRead is not None:
        q = q.where(Message.is_read == isRead)
        count_q = count_q.where(Message.is_read == isRead)

    total = (await db.execute(count_q)).scalar() or 0
    q = q.order_by(Message.created_at.desc()).offset((page - 1) * pageSize).limit(pageSize)
    result = await db.execute(q)
    items = result.scalars().all()

    user_cache: dict[str, str] = {}
    if is_super and items:
        uids = list({m.user_id for m in items})
        users_res = await db.execute(select(User.id, User.username).where(User.id.in_(uids)))
        for row in users_res.all():
            user_cache[row[0]] = row[1] or ""

    out_items = [
        _to_notification_item(m, receiver_username=user_cache.get(m.user_id) if is_super else None)
        for m in items
    ]
    return R.ok(data={"items": out_items, "total": total})


@router.get("/unread", response_model=R[list])
async def message_unread(db: DbSession, current_user: CurrentUser, limit: int = Query(20, le=50)):
    from sqlalchemy import select

    q = (
        select(Message)
        .where(Message.user_id == current_user.id, Message.is_read == 0)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(q)
    items = result.scalars().all()
    return R.ok(data=[_to_notification_item(m) for m in items])


@router.post("/read/{message_id}")
async def message_read(message_id: str, db: DbSession, current_user: CurrentUser):
    from sqlalchemy import select

    q = select(Message).where(Message.id == message_id)
    if not await _is_super_admin(db, current_user.id):
        q = q.where(Message.user_id == current_user.id)
    result = await db.execute(q)
    m = result.scalars().first()
    if m:
        m.is_read = 1
        await db.flush()
    return R.ok()


@router.post("/read-all")
async def message_read_all(db: DbSession, current_user: CurrentUser):
    from sqlalchemy import update

    await db.execute(update(Message).where(Message.user_id == current_user.id).values(is_read=1))
    await db.flush()
    return R.ok()


@router.delete("/{message_id}")
async def message_delete(message_id: str, db: DbSession, current_user: CurrentUser):
    from sqlalchemy import select

    q = select(Message).where(Message.id == message_id)
    if not await _is_super_admin(db, current_user.id):
        q = q.where(Message.user_id == current_user.id)
    result = await db.execute(q)
    m = result.scalars().first()
    if m:
        await db.delete(m)
    return R.ok()


@router.post("/clear")
async def message_clear(db: DbSession, current_user: CurrentUser, userId: str | None = None):
    from sqlalchemy import delete

    if await _is_super_admin(db, current_user.id) and userId:
        target_id = userId
    else:
        target_id = current_user.id
    await db.execute(delete(Message).where(Message.user_id == target_id))
    return R.ok()


class MessageCreateIn(BaseModel):
    title: str
    message: str
    avatar: str | None = None
    link: str | None = None


class MessagePublishIn(BaseModel):
    title: str
    message: str
    link: str | None = None
    roleIds: list[str] = []
    userIds: list[str] = []
    sendToAll: bool = False


@router.post("/publish", response_model=R[dict])
async def message_publish(data: MessagePublishIn, db: DbSession, current_user: CurrentUser):
    if not await _is_super_admin(db, current_user.id):
        raise HTTPException(status_code=403, detail="仅超级管理员可发布消息")
    from sqlalchemy import select
    from app.models.user import User, UserRole

    target_ids: set[str] = set()

    if data.sendToAll:
        r = await db.execute(select(User.id))
        target_ids.update(row[0] for row in r.all())
    else:
        if data.roleIds:
            r = await db.execute(select(UserRole.user_id).where(UserRole.role_id.in_(data.roleIds)))
            target_ids.update(row[0] for row in r.all())
        if data.userIds:
            target_ids.update(data.userIds)

    if not target_ids:
        raise HTTPException(status_code=400, detail="请选择目标角色或用户，或勾选「发布给全部用户」")

    for uid in target_ids:
        m = Message(user_id=uid, title=data.title, message=data.message, link=data.link)
        db.add(m)

    await db.flush()
    return R.ok(data={"count": len(target_ids)})


@router.post("", response_model=R[dict])
async def message_create(data: MessageCreateIn, db: DbSession, current_user: CurrentUser):
    m = Message(
        user_id=current_user.id,
        title=data.title,
        message=data.message,
        avatar=data.avatar,
        link=data.link,
    )
    db.add(m)
    await db.flush()
    return R.ok(data=_to_notification_item(m))
