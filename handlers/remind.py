from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import and_, func, select
from sqlalchemy.orm import selectinload

from states.register_states import RemindStates
from untils.i18n import _
from untils.keyboards import back_menu_markup, cancel_markup, main_menu
from untils.subscriptions import FREE_REMINDER_LIMIT, is_premium_active

from db.orm.models.remind_quote import QuoteRemind
from db.orm.models.user import User
from db.orm.session import AsyncSessionLocal

router = Router()


def _resolve_locale(user: User | None, msg: Message) -> str:
    if user and user.lang_code:
        return user.lang_code.lower()
    return (msg.from_user.language_code or "en").lower()


def _parse_scheduled_time(raw_time: str, tz: ZoneInfo):
    now_in_tz = datetime.now(tz)
    parsed_time = datetime.strptime(raw_time.strip(), "%d.%m %H:%M")
    scheduled_time = parsed_time.replace(year=now_in_tz.year, tzinfo=tz)
    if scheduled_time <= now_in_tz:
        return None
    return scheduled_time


async def _create_reminder_entry(
    conn, user: User, remind_text: str, raw_time: str, locale: str, target
):
    try:
        tz = ZoneInfo(user.timezone)
    except Exception:
        await target.answer(_("TIMEZONE_INVALID", locale=locale))
        return False

    scheduled_time = _parse_scheduled_time(raw_time, tz)
    if not scheduled_time:
        await target.answer(_("REMIND_TIME_INCORRECT", locale=locale))
        return False

    active_reminds = await conn.scalar(
        select(func.count(QuoteRemind.id)).where(
            and_(QuoteRemind.user_id == user.id, QuoteRemind.is_send == False)
        )
    )
    active_reminds = active_reminds or 0

    if not is_premium_active(user) and active_reminds >= FREE_REMINDER_LIMIT:
        await target.answer(
            _("FREE_LIMIT_REACHED", locale=locale).format(limit=FREE_REMINDER_LIMIT)
        )
        return False

    utc_time = scheduled_time.astimezone(timezone.utc)

    exists = await conn.scalar(
        select(QuoteRemind).where(
            and_(
                QuoteRemind.user_id == user.id,
                QuoteRemind.text == remind_text,
                QuoteRemind.time == utc_time,
            )
        )
    )
    if exists:
        await target.answer(_("REMIND_EXIST", locale=locale))
        return False

    new_remind = QuoteRemind(
        user_id=user.id, time=utc_time, timezone=user.timezone, text=remind_text
    )
    conn.add(new_remind)
    await conn.commit()
    await target.answer(_("REMIND_ADDED", locale=locale))
    return True


async def _send_remind_list(target, user: User, locale: str):
    try:
        tz = ZoneInfo(user.timezone)
    except Exception:
        await target.answer(_("TIMEZONE_INVALID", locale=locale))
        return

    async with AsyncSessionLocal() as conn:
        res = await conn.execute(
            select(QuoteRemind)
            .options(selectinload(QuoteRemind.user))
            .where(and_(QuoteRemind.user_id == user.id, QuoteRemind.is_send == False))
            .order_by(QuoteRemind.time)
        )
        reminds = res.scalars().all()

    if not reminds:
        await target.answer(
            _("REMIND_LIST_EMPTY", locale=locale),
            reply_markup=back_menu_markup(locale),
        )
        return

    builder = InlineKeyboardBuilder()
    lines = []
    for r in reminds:
        scheduled_time = r.time
        if scheduled_time.tzinfo is None:
            scheduled_time = scheduled_time.replace(tzinfo=timezone.utc)
        formatted = scheduled_time.astimezone(tz).strftime("%d.%m %H:%M")
        lines.append(
            _("REMIND_LIST_ENTRY", locale=locale).format(
                text=r.text, date=formatted, tz=user.timezone, id=r.id
            )
        )
        builder.row(
            InlineKeyboardButton(
                text=_("BTN_DELETE", locale=locale).format(id=r.id),
                callback_data=f"del_{r.id}",
            )
        )
    builder.row(
        InlineKeyboardButton(
            text=_("BTN_BACK", locale=locale), callback_data="menu_home"
        )
    )
    await target.answer("\n\n".join(lines), reply_markup=builder.as_markup())


@router.message(Command("remind"))
async def remind_cmd(msg: Message):
    async with AsyncSessionLocal() as conn:
        user = await conn.scalar(select(User).where(User.tg_id == msg.from_user.id))

        if not user:
            await msg.answer(_("USER_NOT_REGISTERED"))
            return

        locale = _resolve_locale(user, msg)

        try:
            _, text = msg.text.split(maxsplit=1)
            remind_text, raw_time = text.split(";", maxsplit=1)
            remind_text = remind_text.strip()
            raw_time = raw_time.strip()
        except Exception:
            await msg.answer(_("REMIND_CMD_ERR", locale=locale))
            return

        await _create_reminder_entry(conn, user, remind_text, raw_time, locale, msg)


@router.message(Command("remind_list"))
async def remind_list_cmd(msg: Message):
    async with AsyncSessionLocal() as conn:
        user = await conn.scalar(select(User).where(User.tg_id == msg.from_user.id))

    if not user:
        await msg.answer(_("USER_NOT_REGISTERED"))
        return

    locale = _resolve_locale(user, msg)
    await _send_remind_list(msg, user, locale)


@router.message(Command("dell_remind"))
async def dell_remind_cmd(msg: Message):
    async with AsyncSessionLocal() as conn:
        user = await conn.scalar(select(User).where(User.tg_id == msg.from_user.id))

        if not user:
            await msg.answer(_("USER_NOT_REGISTERED"))
            return

        locale = _resolve_locale(user, msg)

        parts = msg.text.split(maxsplit=1)

        if len(parts) < 2:
            await msg.answer(_("DELETE_ID_ERR", locale=locale))
            return

        try:
            remind_id = int(parts[1])
        except Exception:
            await msg.answer(_("DELETE_ID_ERR", locale=locale))
            return

        remind = await conn.scalar(
            select(QuoteRemind).where(
                and_(
                    QuoteRemind.id == remind_id,
                    QuoteRemind.user_id == user.id,
                    QuoteRemind.is_send == False,
                )
            )
        )

        if not remind:
            await msg.answer(_("REMIND_NOT_FOUND", locale=locale))
            return

        await conn.delete(remind)
        await conn.commit()

        await msg.answer(_("REMIND_DELETED", locale=locale))


@router.callback_query(F.data == "menu_create")
async def menu_create(callback: CallbackQuery, state: FSMContext):
    async with AsyncSessionLocal() as conn:
        user = await conn.scalar(select(User).where(User.tg_id == callback.from_user.id))

    if not user:
        await callback.answer()
        await callback.message.answer(_("USER_NOT_REGISTERED"))
        return

    locale = _resolve_locale(user, callback.message)
    await state.set_state(RemindStates.text)
    await callback.answer()
    await callback.message.answer(
        _("ASK_REMIND_TEXT", locale=locale), reply_markup=cancel_markup(locale)
    )


@router.message(RemindStates.text)
async def remind_text_received(msg: Message, state: FSMContext):
    text = (msg.text or "").strip()
    async with AsyncSessionLocal() as conn:
        user = await conn.scalar(select(User).where(User.tg_id == msg.from_user.id))

    if not user:
        await msg.answer(_("USER_NOT_REGISTERED"))
        await state.clear()
        return

    locale = _resolve_locale(user, msg)

    if not text:
        await msg.answer(_("ASK_REMIND_TEXT", locale=locale), reply_markup=cancel_markup(locale))
        return

    await state.update_data(remind_text=text)
    await state.set_state(RemindStates.time)
    await msg.answer(
        _("ASK_REMIND_TIME", locale=locale), reply_markup=cancel_markup(locale)
    )


@router.message(RemindStates.time)
async def remind_time_received(msg: Message, state: FSMContext):
    raw_time = (msg.text or "").strip()
    data = await state.get_data()
    remind_text = data.get("remind_text", "").strip()

    async with AsyncSessionLocal() as conn:
        user = await conn.scalar(select(User).where(User.tg_id == msg.from_user.id))
        if not user:
            await msg.answer(_("USER_NOT_REGISTERED"))
            await state.clear()
            return

        locale = _resolve_locale(user, msg)

        if not remind_text:
            await msg.answer(_("ASK_REMIND_TEXT", locale=locale), reply_markup=cancel_markup(locale))
            await state.set_state(RemindStates.text)
            return

        created = await _create_reminder_entry(
            conn, user, remind_text, raw_time, locale, msg
        )

    if created:
        await state.clear()
        await msg.answer(_("MENU_PROMPT", locale=locale), reply_markup=main_menu(locale))


@router.callback_query(F.data == "menu_list")
async def menu_list(callback: CallbackQuery):
    async with AsyncSessionLocal() as conn:
        user = await conn.scalar(select(User).where(User.tg_id == callback.from_user.id))

    if not user:
        await callback.answer()
        await callback.message.answer(_("USER_NOT_REGISTERED"))
        return

    locale = _resolve_locale(user, callback.message)
    await callback.answer()
    await _send_remind_list(callback.message, user, locale)


@router.callback_query(F.data.startswith("del_"))
async def delete_remind_callback(callback: CallbackQuery):
    try:
        remind_id = int(callback.data.split("_")[1])
    except Exception:
        await callback.answer()
        return

    async with AsyncSessionLocal() as conn:
        user = await conn.scalar(select(User).where(User.tg_id == callback.from_user.id))

        if not user:
            await callback.answer()
            await callback.message.answer(_("USER_NOT_REGISTERED"))
            return

        locale = _resolve_locale(user, callback.message)

        remind = await conn.scalar(
            select(QuoteRemind).where(
                and_(
                    QuoteRemind.id == remind_id,
                    QuoteRemind.user_id == user.id,
                    QuoteRemind.is_send == False,
                )
            )
        )

        if not remind:
            await callback.answer(_("REMIND_NOT_FOUND", locale=locale))
            return

        await conn.delete(remind)
        await conn.commit()

    await callback.answer()
    await callback.message.answer(
        _("REMIND_DELETED", locale=locale), reply_markup=back_menu_markup(locale)
    )
