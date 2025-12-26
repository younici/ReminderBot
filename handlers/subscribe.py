import os
from datetime import timezone

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, LabeledPrice, Message, PreCheckoutQuery
from sqlalchemy import select

from db.orm.models.user import User
from db.orm.session import AsyncSessionLocal
from untils.i18n import _, normalize_locale
from untils.cleanup import show_menu
from untils.subscriptions import (
    SUBSCRIPTION_DESCRIPTION,
    SUBSCRIPTION_PAYLOAD,
    SUBSCRIPTION_PRICE_STARS,
    SUBSCRIPTION_TITLE,
    extend_subscription,
    is_premium_active,
)

router = Router()

STARS_PROVIDER_TOKEN = os.getenv("STARS_PROVIDER_TOKEN", "")


def _resolve_locale(user: User | None, msg: Message) -> str:
    if user and user.lang_code:
        return normalize_locale(user.lang_code)
    return normalize_locale(msg.from_user.language_code)


async def _send_invoice(message: Message, user: User, locale: str):
    if is_premium_active(user):
        expires = user.premium_until
        if expires and expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires:
            formatted = expires.astimezone(timezone.utc).strftime("%d.%m %H:%M UTC")
        else:
            formatted = "∞"
        await message.answer(_("SUB_ALREADY_ACTIVE", locale=locale).format(date=formatted))
        return

    await message.answer(
        _("SUB_PROMPT", locale=locale).format(price=SUBSCRIPTION_PRICE_STARS)
    )

    prices = [
        LabeledPrice(
            label=_("PREMIUM_LABEL", locale=locale), amount=SUBSCRIPTION_PRICE_STARS
        )
    ]

    title = _("SUBSCRIPTION_TITLE", locale=locale)
    if title == "SUBSCRIPTION_TITLE":
        title = SUBSCRIPTION_TITLE

    description = _("SUBSCRIPTION_DESCRIPTION", locale=locale)
    if description == "SUBSCRIPTION_DESCRIPTION":
        description = SUBSCRIPTION_DESCRIPTION

    try:
        await message.answer_invoice(
            title=title,
            description=description,
            payload=SUBSCRIPTION_PAYLOAD,
            currency="XTR",
            prices=prices,
            start_parameter="reminderbot_subscribe",
            provider_token=STARS_PROVIDER_TOKEN,
        )
    except Exception as e:
        await message.answer(_("SUB_INVOICE_ERROR", locale=locale))
        print(f"Failed to send invoice: {e}")


@router.message(Command("subscribe"))
async def subscribe_cmd(msg: Message):
    await msg.delete()
    await msg.answer(_("USE_MENU", locale=normalize_locale(msg.from_user.language_code)))


@router.callback_query(F.data == "menu_subscribe")
async def menu_subscribe(callback: CallbackQuery):
    async with AsyncSessionLocal() as conn:
        user = await conn.scalar(select(User).where(User.tg_id == callback.from_user.id))

    if not user:
        await callback.answer()
        await callback.message.answer(_("USER_NOT_REGISTERED"))
        return

    locale = _resolve_locale(user, callback.message)
    await callback.answer()
    await _send_invoice(callback.message, user, locale)


@router.pre_checkout_query()
async def pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment_handler(msg: Message):
    if msg.successful_payment.invoice_payload != SUBSCRIPTION_PAYLOAD:
        return

    async with AsyncSessionLocal() as conn:
        user = await conn.scalar(select(User).where(User.tg_id == msg.from_user.id))

        if not user:
            await msg.answer(_("USER_NOT_REGISTERED"))
            return

        new_until = extend_subscription(user)
        conn.add(user)
        await conn.commit()

    locale = _resolve_locale(user, msg)
    if new_until.tzinfo is None:
        new_until = new_until.replace(tzinfo=timezone.utc)

    formatted = new_until.astimezone(timezone.utc).strftime("%d.%m %H:%M UTC")
    await msg.answer(_("SUB_SUCCESS", locale=locale).format(date=formatted))
