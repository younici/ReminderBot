from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from untils.i18n import _

router = Router()

AVAILABLE_LANGS = {
    "en": "English",
    "ru": "Русский",
    "uk": "Українська",
}

@router.message(Command("language"))
async def choose_language(message: Message):
    builder = InlineKeyboardBuilder()
    for code, name in AVAILABLE_LANGS.items():
        builder.add(InlineKeyboardButton(text=name, callback_data=f"lang_{code}"))
    builder.adjust(1)

    await message.answer(
        text=_("CHOOSE_LANGUAGE"),
        reply_markup=builder.as_markup()
    )

@router.callback_query(F.data.startswith("lang_"))
async def language_changed(callback: CallbackQuery):
    lang_code = callback.data.split("_")[1]
    await callback.answer()
    await callback.message.answer(_("LANGUAGE_CHANGED", locale=lang_code))
    await callback.message.delete()
