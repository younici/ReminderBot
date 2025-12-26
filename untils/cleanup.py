import asyncio
from typing import Dict

menu_messages: Dict[int, int] = {}


async def safe_delete(message):
    try:
        await message.delete()
    except Exception:
        pass


async def safe_delete_after(message, delay: int = 5):
    await asyncio.sleep(delay)
    await safe_delete(message)


async def show_menu(message, text: str, reply_markup):
    chat_id = message.chat.id
    bot = message.bot

    old_msg_id = menu_messages.get(chat_id)
    if old_msg_id:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=old_msg_id)
        except Exception:
            pass

    sent = await message.answer(text, reply_markup=reply_markup)
    menu_messages[chat_id] = sent.message_id
    return sent
