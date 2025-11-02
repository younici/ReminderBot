import os
from dotenv import load_dotenv
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from untils.redis_db import preload_keys, init_redis

from untils.i18n import i18n_middleware

from db.orm.until import init_db

load_dotenv()
token = os.getenv("BOT_TOKEN")

bot = Bot(token=token)
dp = None

from handlers import remind, start, language

async def main():
    global dp

    await init_db()
    redis_client = await init_redis()

    if not redis_client:
        print(bool(redis_client))
        print("redis not initialized")
        return

    storage = RedisStorage(redis=redis_client)
    dp = Dispatcher(storage=storage)

    await preload_keys()

    dp.message.middleware(i18n_middleware)
    dp.callback_query.middleware(i18n_middleware)

    dp.include_routers(remind.router, start.router, language.router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

