from django.apps import AppConfig

import logging

from .token import alcala_es_musica_bot_token
import locale


bot = None
dispatcher = None

class BotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bot'
    verbose_name = "Agenda musical de Alcalá de Henares"

    def ready(self):

        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        locale.setlocale(locale.LC_ALL, "es_ES.UTF-8")

        self.setup(alcala_es_musica_bot_token)


    def setup(self, token):
        # Create bot, update queue and dispatcher instances

        from telegram.ext import CommandHandler, Filters, MessageHandler, CallbackQueryHandler
        from telegram import Bot
        from telegram.ext import Dispatcher

        from bot.views import handlers

        global bot
        bot = Bot(token)

        global dispatcher
        dispatcher = Dispatcher(bot, None, workers=0, use_context=True)

        dispatcher.add_handler(CommandHandler('start', handlers.start))
        # dispatcher.add_handler(CommandHandler('eventos', handlers.events))
        # dispatcher.add_handler(CommandHandler('finde', handlers.finde))
        # dispatcher.add_handler(CommandHandler('suscripciones', handlers.subscriptions))
        # dispatcher.add_handler(CommandHandler('subscripciones', handlers.subscriptions))
        # dispatcher.add_handler(CallbackQueryHandler(handlers.callback_subscriptions))

        # dispatcher.add_handler(MessageHandler(Filters.text, handlers.other_text))

        dispatcher.add_error_handler(error_callback)


# https://github.com/python-telegram-bot/python-telegram-bot/wiki/Exception-Handling
def error_callback(update, context):

    from telegram.error import (TelegramError, Unauthorized, BadRequest,
                                TimedOut, ChatMigrated, NetworkError)

    # try:
    raise context.error
    # except Unauthorized:
    #     # remove update.message.chat_id from conversation list
    # except BadRequest:
    #     # handle malformed requests - read more below!
    # except TimedOut:
    #     # handle slow connection problems
    # except NetworkError:
    #     # handle other connection problems
    # except ChatMigrated as e:
    #     # the chat_id of a group has changed, use e.new_chat_id instead
    # except TelegramError:
    #     # handle all other telegram related errors

