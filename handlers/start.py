from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

from timezonefinder import TimezoneFinder

from db.orm.session import AsyncSessionLocal
from db.orm.models.user import User
from sqlalchemy import select

from untils.i18n import _

from states.register_states import RegisterStates
from untils.redis_db import get_redis_client

redis = get_redis_client()

router = Router()

_tf = TimezoneFinder(in_memory=True)

@router.message(CommandStart())
async def start_cmd(msg: Message, state: FSMContext):
    async with AsyncSessionLocal() as conn:
        res = await conn.execute(select(User).where(User.tg_id == msg.from_user.id))
        user = res.scalar_one_or_none()
        if not user:
            kb = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text=_("SEND_LOCATION"), request_location=True)]
                ],
                resize_keyboard=True,
                one_time_keyboard=True
            )

            await msg.answer(_("GREETING"), reply_markup=kb)
            await state.set_state(RegisterStates.location)
        else:
            await msg.answer(_("GREETING", locale=user.lang_code))

@router.message(Command("help"))
async def help_cmd(msg: Message):
    global redis
    if not redis:
        redis = get_redis_client()

    await msg.answer(_("HELP_ANSWER", locale=await redis.get(f"user:{msg.from_user.id}:lang")))

@router.message(RegisterStates.location)
async def set_location(msg: Message, state: FSMContext):
    if msg.location:
        async with AsyncSessionLocal() as conn:
            result =  await conn.execute(select(User).where(User.tg_id == msg.from_user.id))
            usr = result.scalar_one_or_none()
            if not usr:
                lat = msg.location.latitude
                lon = msg.location.longitude


                timezone = _tf.timezone_at(lat=lat, lng=lon)
                await msg.answer(f"{timezone}", reply_markup=ReplyKeyboardRemove())
                await state.clear()
                user = User(tg_id=msg.from_user.id, lang_code=msg.from_user.language_code, timezone=timezone)

                await redis.set(f"user:{msg.from_user.id}:lang", msg.from_user.language_code)

                conn.add(user)
                await conn.commit()
            else:
                await msg.answer(_("ALREADY_REGISTERED", locale=usr.lang_code), reply_markup=ReplyKeyboardRemove())
    else:
        await msg.answer(_("GET_LOCATION_ERR"), await redis.get(f"user:{msg.from_user.id}:lang"))