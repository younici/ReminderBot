from db.orm.session import AsyncSessionLocal
from db.orm.models.remind_quote import QuoteRemind
from sqlalchemy import select, and_

from datetime import datetime

from aiogram import Bot

async def reminder_loop(bot: Bot):
    async with AsyncSessionLocal() as conn:
        while True:
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
                pass