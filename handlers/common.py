# from aiogram import Router
# from aiogram.types import Message
# from aiogram.filters import Command
# from aiogram.fsm.context import FSMContext
#
# from untils.i18n import _
#
# router = Router()
#
# @router.message(Command("cancel"))
# async def cancel_cmd(msg: Message, state: FSMContext):
#     if await state.get_state() is None:
#         await msg.answer(_("NONE_STATE"))
#     else:
#         await msg.answer(_("STATE_CLEAR"))
#         await state.clear()