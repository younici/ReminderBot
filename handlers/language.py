from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from untils.i18n import _, normalize_locale
from untils.cleanup import safe_delete, safe_delete_after, show_menu
from untils.keyboards import main_menu

from db.orm.session import AsyncSessionLocal
from db.orm.models.user import User
from sqlalchemy import select

router = Router()

AVAILABLE_LANGS = {
    "en": "English",
    "ru": "Русский",
    "uk": "Українська",
}

def _language_keyboard(locale: str):
    builder = InlineKeyboardBuilder()
    for code, name in AVAILABLE_LANGS.items():
        builder.add(InlineKeyboardButton(text=name, callback_data=f"lang_{code}"))
    builder.adjust(1)
    builder.row(
        InlineKeyboardButton(text=_("BTN_BACK", locale=locale), callback_data="menu_home")
    )
    return builder.as_markup()


@router.message(Command("language"))
async def choose_language(msg: Message):
    await msg.delete()
    locale = normalize_locale(msg.from_user.language_code)
    await show_menu(msg, _("MENU_PROMPT", locale=locale), main_menu(locale))


@router.callback_query(F.data == "menu_language")
async def choose_language_menu(callback: CallbackQuery):
    async with AsyncSessionLocal() as conn:
        res = await conn.execute(select(User).where(User.tg_id == callback.from_user.id))

        await safe_delete(callback.message)

        user = res.scalar_one_or_none()

        if user:
            await callback.answer()
            await callback.message.answer(
                text=_("CHOOSE_LANGUAGE", locale=user.lang_code),
                reply_markup=_language_keyboard(normalize_locale(user.lang_code)),
            )
        else:
            await callback.answer()
            await callback.message.answer(_("USER_NOT_REGISTERED"))

@router.callback_query(F.data.startswith("lang_"))
async def language_changed(callback: CallbackQuery):
    async with AsyncSessionLocal() as conn:
        res = await conn.execute(select(User).where(User.tg_id == callback.from_user.id))
        user = res.scalar_one_or_none()

        if user:
            lang_code = callback.data.split("_")[1]

            user.lang_code = lang_code
            await conn.commit()

            locale = normalize_locale(lang_code)
            await callback.answer(_("LANGUAGE_CHANGED", locale=locale))
            await safe_delete(callback.message)
            await show_menu(callback.message, _("MENU_PROMPT", locale=locale), main_menu(locale))
        else:
            await callback.answer(_("USER_NOT_REGISTERED"))
