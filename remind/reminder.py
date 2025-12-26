import asyncio
from datetime import datetime, timezone

from aiogram import Bot
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.orm.models.remind_quote import QuoteRemind
from db.orm.session import AsyncSessionLocal


async def reminder_loop(bot: Bot):
    while True:
        async with AsyncSessionLocal() as conn:
            now = datetime.now(timezone.utc)

            result = await conn.execute(
                select(QuoteRemind)
                .options(selectinload(QuoteRemind.user))
                .where(QuoteRemind.is_send == False)
            )

            reminds = result.scalars().all()
            for r in reminds:
                scheduled_time = r.time
                if scheduled_time.tzinfo is None:
                    scheduled_time = scheduled_time.replace(tzinfo=timezone.utc)

                if scheduled_time > now:
                    continue

                chat_id = r.user.tg_id if r.user else None

                if not chat_id:
                    print(f"не удалось найти tg_id для напоминания {r.id}")
                else:
                    try:
                        await bot.send_message(chat_id=chat_id, text=r.text)
                    except Exception as e:
                        print(
                            f"не удалось отправить сообщение для {chat_id} \n\n {e.with_traceback(e.__traceback__)}"
                        )

                r.is_send = True

            await conn.commit()
        await asyncio.sleep(30)
