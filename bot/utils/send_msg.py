from bot.models.user_chat import UserChat
from bot.dev_config import *
import telegram
import time
from threading import Thread


def send_to_all_thread(bot, message):

    if developing:
        user_chats = UserChat.objects.filter(id_chat=dev_chat_id)
    else:
        user_chats = UserChat.objects.filter(is_active=True)

    for user_chat in user_chats:
        time.sleep(0.3)
        chat_id = user_chat.id_chat

        try:
            bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML",
                         disable_web_page_preview=True, reply_markup=telegram.ReplyKeyboardRemove())
        except telegram.error.Unauthorized:
            user_chat.is_active = False

        user_chat.save()

def send_to_all(bot, message):
    thread = Thread(target=send_to_all_thread, args = (bot, message))
    thread.start()



def send_photo_to_all_thread(bot, photo, caption, reply_markup, initial_text=None):

    if developing:
        user_chats = UserChat.objects.filter(id_chat=dev_chat_id)
    else:
        user_chats = UserChat.objects.filter(is_active=True)

    for user_chat in user_chats:
        time.sleep(0.3)
        chat_id = user_chat.id_chat

        try:
            if initial_text:
                bot.send_message(chat_id=chat_id, text=initial_text, parse_mode="HTML", disable_web_page_preview=True)
            bot.send_photo(chat_id=chat_id, photo=photo, caption=caption, parse_mode="HTML", reply_markup=reply_markup)
        except telegram.error.Unauthorized:
            user_chat.is_active = False

        user_chat.save()

def send_photo_to_all(bot, photo, caption, reply_markup, initial_text=None):
    thread = Thread(target=send_photo_to_all_thread, args = (bot, photo, caption, reply_markup, initial_text))
    thread.start()


def send_dev_chat_message(bot, message):
    bot.send_message(chat_id=dev_chat_id, text='AemBot dev message:\n' + message)
