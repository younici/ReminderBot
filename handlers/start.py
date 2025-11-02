from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

import requests

from db.orm.session import AsyncSessionLocal
from db.orm.models.user import User
from sqlalchemy import select

from untils.i18n import _

from states.register_states import RegisterStates

router = Router()

@router.message(CommandStart())
async def start_cmd(msg: Message, state: FSMContext):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=_("SEND_LOCATION"), request_location=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await msg.answer(_("GREETING"), reply_markup=kb)
    await state.set_state(RegisterStates.location)

@router.message(Command("help"))
async def help_cmd(msg: Message):
    await msg.answer(_("HELP_ANSWER"))

@router.message(RegisterStates.location)
async def set_location(msg: Message, state: FSMContext):
    if msg.location:
        async with AsyncSessionLocal() as conn:
            result =  await conn.execute(select(User).where(User.tg_id == msg.from_user.id))
            usr = result.scalar_one_or_none()
            if not usr:
                lat = msg.location.latitude
                lon = msg.location.longitude
                r = requests.get(f"https://timeapi.io/api/TimeZone/coordinate?latitude={lat}&longitude={lon}")
                timezone = r.json()['timeZone']
                await msg.answer(f"{timezone}", reply_markup=ReplyKeyboardRemove())
                await state.clear()

                user = User(tg_id=msg.from_user.id, lang_code=msg.from_user.language_code, timezone=timezone)

                conn.add(user)
                await conn.commit()
            else:
                await msg.answer(_("ALREADY_REGISTERED"), reply_markup=ReplyKeyboardRemove())
    else:
        await msg.answer(_("GET_LOCATION_ERR"))