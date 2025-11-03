from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from untils.i18n import _

from db.orm.models.user import User
from db.orm.models.remind_quote import QuoteRemind
from db.orm.session import AsyncSessionLocal
from sqlalchemy import select

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

        remind = QuoteRemind(user_id=msg.from_user.id,
                            time=utc_time,
                            timezone=user.timezone,
                            text=remind_text)

        conn.add(remind)
        await conn.commit()
        await msg.answer(_(f"REMIND_ADDED", locale=user.lang_code))