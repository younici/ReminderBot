from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from untils.i18n import _

from db.orm.models.user import User
from db.orm.models.remind_quote import QuoteRemind
from db.orm.session import AsyncSessionLocal
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from untils.redis_db import get_redis_client

router = Router()

redis = get_redis_client()

@router.message(Command("remind"))
async def remind_cmd(msg: Message):
    async with AsyncSessionLocal() as conn:
        res = await conn.execute(select(User).where(User.tg_id == msg.from_user.id))
        user = res.scalar_one_or_none()

        if not user:
            await msg.answer(_("USER_NOT_REGISTERED"))
            return

        remind_text = ""
        time = datetime.utcnow()

        try:
            text = msg.text.split(maxsplit=1)

            remind_text = text[1].split(sep=";")[0]
            time = datetime.strptime(text[1].split(sep=";")[1].lstrip(), "%d.%m %H:%M")
        except Exception:
            await msg.answer(_("REMIND_CMD_ERR", locale=user.lang_code))
            return

        time = time.replace(year=datetime.utcnow().year)

        tz = ZoneInfo(user.timezone)
        time = time.replace(tzinfo=tz)

        utc_time = time.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)

        if time <= datetime.now(tz=tz):
            await msg.answer(_("REMIND_TIME_INCORRECT", locale=user.lang_code))
            return

        new_remind = QuoteRemind(user_id=user.id,
                            time=utc_time,
                            timezone=user.timezone,
                            text=remind_text)

        res = await conn.execute(select(QuoteRemind).where(
            and_(
                QuoteRemind.user_id == user.id,
                QuoteRemind.text == new_remind.text,
                QuoteRemind.time == new_remind.time)
        ))

        if res.scalar_one_or_none():
            await msg.answer(_("REMIND_EXIST", locale=user.lang_code))
            return

        conn.add(new_remind)
        await conn.commit()
        await msg.answer(_(f"REMIND_ADDED", locale=user.lang_code))

@router.message(Command("remind_list"))
async def remind_list_cmd(msg: Message):
    async with AsyncSessionLocal() as conn:
        result = await conn.execute(select(User)
                                    .options(selectinload(User.remind_list))
                                    .where(User.tg_id == msg.from_user.id))
        user = result.scalar_one_or_none()

        if not user:
            await msg.answer(_("USER_NOT_REGISTERED"))
            return

        text = f""

        for r in user.remind_list:
            if r.is_send:
                continue

            formatted = r.time.strftime("%d.%m %H:%M")

            text += f"\ntext: {r.text}\ndate: {formatted}\nid: {r.id}"
        if text:
            await msg.answer(text)
        else:
            await msg.answer("none")

@router.message(Command("dell_remind"))
async def dell_remind_cmd(msg: Message):
    async with AsyncSessionLocal() as conn:
        res = await conn.execute(select(User).where(User.tg_id == msg.from_user.id))

        user = res.scalar_one_or_none()

        if not user:
            await msg.answer(_("USER_NOT_REGISTERED"))
            return

        text = msg.text.split(maxsplit=1)
        id = 0

        if len(text) < 2:
            await msg.answer(_("DELETE_ID_ERR", locale=user.lang_code))

        try:
            id = int(text[1])
        except Exception:
            await msg.answer(_("DELETE_ID_ERR", locale=user.lang_code))
            return

        res = await conn.execute(select(QuoteRemind).where(QuoteRemind.id == id))

        remind = res.scalar_one_or_none()

        if not remind:
            await msg.answer(_("REMIND_BOT_FOUND", locale=user.lang_code))
            return

        await conn.delete(remind)
        await conn.commit()

        await msg.answer(_("REMIND_DELETED", locale=user.lang_code))