from bot.models.user_chat import UserChat
from bot.token import *
import telegram
import time


def send_to_all(bot, message):
    if developing:
        user_chats = UserChat.objects.filter(id_chat=dev_chat_id)
    else:
        user_chats = UserChat.objects.all()

    for user_chat in user_chats:
        time.sleep(0.3)
        chat_id = user_chat.id_chat
        bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML",
                         disable_web_page_preview=True, reply_markup=telegram.ReplyKeyboardRemove())
