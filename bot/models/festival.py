
from bot.bot_config import URL_BASE
from datetime import datetime
import json


class Festival:

    def __init__(self, id, title, profile_image, start_date, end_date, slug, news_tag, has_events=True):
        self.id = id
        self.title = title
        self.profile_image = profile_image
        self.start_date = start_date
        self.end_date = end_date
        self.slug = slug
        self.news_tag = news_tag
        self.has_events = has_events

    def get_web_link(self):
        return f'{URL_BASE}/sp/{self.slug}'

    def get_image_url(self):
        return f'{URL_BASE}{self.profile_image}'

    def caption(self):
        return f'<b>{self.title}</b>\n<i>{self.get_dates_human()}</i>'

    def get_dates_human(self):
        if self.start_date and self.end_date:
            start_date = datetime.strptime(self.start_date, "%Y-%m-%d")
            end_date = datetime.strptime(self.end_date, "%Y-%m-%d")
            return start_date.strftime('%d/%m/%Y') + " - " + end_date.strftime('%d/%m/%Y')
        elif self.start_date:
            start_date = datetime.strptime(self.start_date, "%Y-%m-%d")
            return start_date.strftime('%d/%m/%Y')
        else:
            return ""

    def is_active(self):
        if self.end_date:
            end_date = datetime.strptime(self.end_date, "%Y-%m-%d")
            return datetime.now() <= end_date
        elif self.start_date:
            start_date = datetime.strptime(self.start_date, "%Y-%m-%d")
            return datetime.now() <= start_date
        else:
            return False

    @staticmethod
    def parse(festivals_json):
        festivals_api = json.loads(festivals_json)['microsites']
        festivals = []
        for fest_api in festivals_api:
            fest = Festival(
                fest_api['id'],
                fest_api['title'],
                fest_api['profile_image'] or fest_api['top_image'] ,
                fest_api['start_date'],
                fest_api['end_date'],
                fest_api['slug'],
                fest_api['news_tag'],
            )

            if fest.is_active():
                from bot.views.events import get_festival_events
                fest.has_events = len(get_festival_events(fest.id)) > 0
                festivals.append(fest)

        return festivals


