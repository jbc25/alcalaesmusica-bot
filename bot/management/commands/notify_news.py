from django.core.management.base import BaseCommand

from bot.utils.send_msg import send_to_all
from bot.views.events import *
from bot.views.news import *


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
        send_to_all(bot, text_new_news)

