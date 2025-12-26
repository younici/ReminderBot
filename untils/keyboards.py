from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from untils.i18n import _


def main_menu(locale: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=_("BTN_CREATE", locale=locale), callback_data="menu_create"
        ),
        InlineKeyboardButton(
            text=_("BTN_LIST", locale=locale), callback_data="menu_list"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=_("BTN_TIMEZONE", locale=locale), callback_data="menu_timezone"
        ),
        InlineKeyboardButton(
            text=_("BTN_LANGUAGE", locale=locale), callback_data="menu_language"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=_("BTN_SUBSCRIBE", locale=locale), callback_data="menu_subscribe"
        ),
        InlineKeyboardButton(
            text=_("BTN_HELP", locale=locale), callback_data="menu_help"
        ),
    )
    return builder.as_markup()


def cancel_markup(locale: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=_("BTN_CANCEL", locale=locale), callback_data="cancel"
        ),
        InlineKeyboardButton(
            text=_("BTN_BACK", locale=locale), callback_data="menu_home"
        ),
    )
    return builder.as_markup()


def back_menu_markup(locale: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=_("BTN_BACK", locale=locale), callback_data="menu_home")
    )
    return builder.as_markup()
