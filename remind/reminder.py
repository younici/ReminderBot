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
                await bot.send_message(chat_id=r.user_id, text=r.text)
                r.is_send = True

            await conn.commit()
        await asyncio.sleep(30)