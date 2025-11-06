import asyncio

from db.orm.session import AsyncSessionLocal
from db.orm.models.remind_quote import QuoteRemind
from sqlalchemy import select, and_

from datetime import datetime

from aiogram import Bot

async def reminder_loop(bot: Bot):
    while True:
        async with AsyncSessionLocal() as conn:
            now = datetime.utcnow()

            query = select(QuoteRemind).where(
                and_(
                    QuoteRemind.is_send == False,
                    QuoteRemind.time <= now
                )
            )

            result = await conn.execute(query)

            reminds = result.scalars().all()
            for r in reminds:
                try:
                    await bot.send_message(chat_id=r.user_id, text=r.text)
                except Exception as e:
                    print(f"не удалось отправить сообщение для {r.user_id} \n\n {e.with_traceback(e.__traceback__)}")

                r.is_send = True

            await conn.commit()
        await asyncio.sleep(30)