from datetime import datetime

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from untils.i18n import _

router = Router()

@router.message(Command("remind"))
async def remind_cmd(msg: Message):
    remind_text = ""
    time = datetime.utcnow()

    try:
        text = msg.text.split(maxsplit=1)

        remind_text = text[1].split(sep=";")[0]
        time = datetime.strptime(text[1].split(sep=";")[1].lstrip(), "%d.%m %H:%M")
    except Exception:
        await msg.answer(_("REMIND_CMD_ERR").format(lang=msg.from_user.language_code))
        return

    print(f"text for remind: {remind_text}\ntime: {time}")