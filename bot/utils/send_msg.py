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


def send_photo_to_all(bot, photo, caption, reply_markup, initial_text=None):
    if developing:
        user_chats = UserChat.objects.filter(id_chat=dev_chat_id)
    else:
        user_chats = UserChat.objects.all()

    for user_chat in user_chats:
        time.sleep(0.3)
        chat_id = user_chat.id_chat
        if initial_text:
            bot.send_message(chat_id=chat_id, text=initial_text, parse_mode="HTML", disable_web_page_preview=True)

        try:
            bot.send_photo(chat_id=chat_id, photo=photo, caption=caption, parse_mode="HTML", reply_markup=reply_markup)
        except telegram.error.TelegramError as e:
            send_dev_chat_message(bot, "Error al notificar festival: {}\nError:\n{}".format(caption, e))


def send_dev_chat_message(bot, message):
    bot.send_message(chat_id=dev_chat_id, text='AemBot dev message:\n' + message)
