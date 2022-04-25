import json

from django.core.management.base import BaseCommand

from bot.models.tag import Tag
from bot.models.user_chat import UserChat
from bot.models.event_notices import *
from bot.views.events import *
from bot.views.news import *
from bot.utils.messages import *
import time
from bot.token import *


class Command(BaseCommand):
    help = 'Notify new news to users (for cron jobs)'

    # def add_arguments(self, parser):
    #     parser.add_argument('jsonfile', type=str, help='Indicates the JSON file to export entities')

    def handle(self, *args, **options):

        from bot.apps import bot

        news_list = get_news_api()
        if not news_list:
            return

        notified_news_ids = json.loads(Preference.get(PREF_NOTIFIED_NEWS_IDS, '[]'))

        news_notify = []

        for news in news_list:
            if news.id not in notified_news_ids:
                news_notify.append(news)
                notified_news_ids.append(news.id)

        if not news_notify:
            print('No news to notify')
            return

        Preference.set(PREF_NOTIFIED_NEWS_IDS, json.dumps(notified_news_ids))

        text_new_news = '<b>¡Noticias frescas!</b>' + news_list_info(news_notify)

        if developing:
            user_chats = UserChat.objects.filter(id_chat=dev_chat_id)
        else:
            user_chats = UserChat.objects.all()

        for user_chat in user_chats:
            time.sleep(0.3)
            chat_id = user_chat.id_chat
            bot.send_message(chat_id=chat_id, text=text_new_news, parse_mode="HTML",
                             disable_web_page_preview=True, reply_markup=telegram.ReplyKeyboardRemove())

