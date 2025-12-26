import asyncio
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select

from db.orm.models.user import User
from db.orm.session import AsyncSessionLocal
from states.register_states import RegisterStates, TimezoneStates
from untils.cleanup import safe_delete, safe_delete_after, show_menu
from untils.i18n import _, normalize_locale
from untils.keyboards import cancel_markup, main_menu
from untils.subscriptions import FREE_REMINDER_LIMIT

router = Router()


@router.message(CommandStart())
async def start_cmd(msg: Message, state: FSMContext):
    async with AsyncSessionLocal() as conn:
        user = await conn.scalar(select(User).where(User.tg_id == msg.from_user.id))

    locale = normalize_locale(user.lang_code if user else msg.from_user.language_code)

    if user and user.timezone:
        await msg.answer(_("GREETING", locale=locale))
        await show_menu(msg, _("MENU_PROMPT", locale=locale), main_menu(locale))
        return
    else:
        # force registration if user is missing or has no timezone
        if user:
            async with AsyncSessionLocal() as conn:
                user.timezone = None
                conn.add(user)
                await conn.commit()

    await state.set_state(RegisterStates.timezone)
    await msg.answer(_("GREETING", locale=locale))
    await msg.answer(_("ASK_TIMEZONE", locale=locale), reply_markup=cancel_markup(locale))


@router.message(Command("help"))
async def help_cmd(msg: Message):
    await msg.delete()
    locale = normalize_locale(msg.from_user.language_code)
    await show_menu(msg, _("MENU_PROMPT", locale=locale), main_menu(locale))


@router.message(Command("menu"))
async def menu_cmd(msg: Message):
    async with AsyncSessionLocal() as conn:
        user = await conn.scalar(select(User).where(User.tg_id == msg.from_user.id))

    if not user:
        await msg.answer(_("USER_NOT_REGISTERED"))
        return

    locale = normalize_locale(user.lang_code)
    await msg.answer(_("MENU_PROMPT", locale=locale), reply_markup=main_menu(locale))


@router.message(Command("timezone"))
async def timezone_cmd(msg: Message, state: FSMContext):
    await msg.delete()
    locale = normalize_locale(msg.from_user.language_code)
    await show_menu(msg, _("MENU_PROMPT", locale=locale), main_menu(locale))


@router.message(RegisterStates.timezone)
async def set_timezone(msg: Message, state: FSMContext):
    locale = normalize_locale(msg.from_user.language_code)

    tz_name = (msg.text or "").strip()

    try:
        ZoneInfo(tz_name)
    except Exception:
        await msg.answer(_("TIMEZONE_INVALID", locale=locale))
        return

    async with AsyncSessionLocal() as conn:
        existing = await conn.scalar(select(User).where(User.tg_id == msg.from_user.id))
        if existing:
            await msg.answer(_("ALREADY_REGISTERED", locale=existing.lang_code or locale))
            await state.clear()
            return

        user = User(tg_id=msg.from_user.id, lang_code=locale, timezone=tz_name)

        conn.add(user)
        await conn.commit()

    await state.clear()
    note = await msg.answer(_("TIMEZONE_SAVED", locale=locale).format(tz=tz_name))
    asyncio.create_task(safe_delete_after(note))
    await show_menu(msg, _("MENU_PROMPT", locale=locale), main_menu(locale))


@router.message(TimezoneStates.timezone)
async def update_timezone(msg: Message, state: FSMContext):
    locale = normalize_locale(msg.from_user.language_code)

    tz_name = (msg.text or "").strip()

    try:
        ZoneInfo(tz_name)
    except Exception:
        await msg.answer(_("TIMEZONE_INVALID", locale=locale))
        return

    async with AsyncSessionLocal() as conn:
        user = await conn.scalar(select(User).where(User.tg_id == msg.from_user.id))

        if not user:
            await msg.answer(_("USER_NOT_REGISTERED"))
            await state.clear()
            return

        user.timezone = tz_name
        conn.add(user)
        await conn.commit()

        locale = user.lang_code or locale

    note = await msg.answer(_("TIMEZONE_UPDATED", locale=locale).format(tz=tz_name))
    asyncio.create_task(safe_delete_after(note))
    await state.clear()
    await show_menu(msg, _("MENU_PROMPT", locale=locale), main_menu(locale))


@router.callback_query(F.data == "menu_home")
async def menu_home(callback: CallbackQuery, state: FSMContext):
    await safe_delete(callback.message)
    async with AsyncSessionLocal() as conn:
        user = await conn.scalar(select(User).where(User.tg_id == callback.from_user.id))

    if not user:
        await callback.answer()
        await callback.message.answer(_("USER_NOT_REGISTERED"))
        return

    locale = normalize_locale(user.lang_code if user else callback.from_user.language_code)
    await state.clear()
    await callback.answer()
    await show_menu(callback.message, _("MENU_PROMPT", locale=locale), main_menu(locale))


@router.callback_query(F.data == "menu_timezone")
async def menu_timezone(callback: CallbackQuery, state: FSMContext):
    await safe_delete(callback.message)
    async with AsyncSessionLocal() as conn:
        user = await conn.scalar(select(User).where(User.tg_id == callback.from_user.id))

    if not user:
        await callback.answer()
        note = await callback.message.answer(_("USER_NOT_REGISTERED"))
        asyncio.create_task(safe_delete_after(note))
        return

    locale = normalize_locale(user.lang_code if user else callback.from_user.language_code)
    await state.set_state(TimezoneStates.timezone)
    await callback.answer()
    await callback.message.answer(
        _("ASK_TIMEZONE_UPDATE", locale=locale).format(tz=user.timezone),
        reply_markup=cancel_markup(locale),
    )


@router.callback_query(F.data == "cancel")
async def cancel_flow(callback: CallbackQuery, state: FSMContext):
    await safe_delete(callback.message)
    async with AsyncSessionLocal() as conn:
        user = await conn.scalar(select(User).where(User.tg_id == callback.from_user.id))

    locale = normalize_locale(user.lang_code if user else callback.from_user.language_code)
    await state.clear()
    await callback.answer(_("ACTION_CANCELLED", locale=locale))

    if user:
        await show_menu(callback.message, _("MENU_PROMPT", locale=locale), main_menu(locale))
    else:
        note = await callback.message.answer(_("USER_NOT_REGISTERED"))
        asyncio.create_task(safe_delete_after(note))
