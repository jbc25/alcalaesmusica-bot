
from bot.bot_config import URL_BASE
from datetime import datetime
import json


DATETIME_FORMAT_API = "%Y-%m-%dT%H:%M:%S"


class News:

    def __init__(self, id, title, subtitle, image, publication_date, slug, status):
        self.id = id
        self.title = title
        self.subtitle = subtitle
        self.image = image
        self.publication_date = publication_date
        self.slug = slug
        self.status = status

    def get_web_link(self):
        return f'{URL_BASE}/blog/{self.date_url()}/{self.slug}'

    def get_image_url(self):
        return f'{URL_BASE}{self.image}'

    def get_publication_date_human(self):
        pub_date = datetime.strptime(self.publication_date, DATETIME_FORMAT_API)
        return pub_date.strftime("%d/%m/%Y %H:%M")

    def date_url(self):
        pub_date = datetime.strptime(self.publication_date, DATETIME_FORMAT_API)
        return pub_date.strftime("%Y/%m/%d")

    @staticmethod
    def parse(news_json):
        list_news_api = json.loads(news_json)['entries']
        news_list = []
        for news_api in list_news_api:
            news = News(
                news_api['id'],
                news_api['title'],
                news_api['lead'],
                news_api['image'],
                news_api['publication_date'],
                news_api['slug'],
                news_api['status'],
            )

            if news.status == 2:   # published
                news_list.append(news)

        news_sorted = sorted(
            news_list,
            key=lambda x: datetime.strptime(x.publication_date, DATETIME_FORMAT_API), reverse=False
        )

        return news_sorted


