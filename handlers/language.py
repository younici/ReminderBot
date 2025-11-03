from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from untils.i18n import _

from db.orm.session import AsyncSessionLocal
from db.orm.models.user import User
from sqlalchemy import select

from untils.redis_db import get_redis_client

redis_client = get_redis_client()

router = Router()

AVAILABLE_LANGS = {
    "en": "English",
    "ru": "Русский",
    "uk": "Українська",
}

@router.message(Command("language"))
async def choose_language(msg: Message):
    async with AsyncSessionLocal() as conn:
        res = await conn.execute(select(User).where(User.tg_id == msg.from_user.id))

        user = res.scalar_one_or_none()

        if user:
            lang_code = await redis_client.get(f"user:{msg.from_user.id}:lang") or user.lang_code or "en"

            builder = InlineKeyboardBuilder()
            for code, name in AVAILABLE_LANGS.items():
                builder.add(InlineKeyboardButton(text=name, callback_data=f"lang_{code}"))
            builder.adjust(1)

            await msg.answer(
                text=_("CHOOSE_LANGUAGE", locale=lang_code),
                reply_markup=builder.as_markup()
            )
        else:
            await msg.answer(_("USER_NOT_REGISTERED"))

@router.callback_query(F.data.startswith("lang_"))
async def language_changed(callback: CallbackQuery):
    async with AsyncSessionLocal() as conn:
        res = await conn.execute(select(User).where(User.tg_id == callback.from_user.id))
        user = res.scalar_one_or_none()

        if user:
            lang_code = callback.data.split("_")[1]

            await callback.answer()
            await callback.message.answer(_("LANGUAGE_CHANGED", locale=lang_code))
            await callback.message.delete()

            await redis_client.set(f"user:{callback.from_user.id}:lang", lang_code)

            user.lang_code = lang_code
            await conn.commit()
        else:
            await callback.answer(_("USER_NOT_REGISTERED"))