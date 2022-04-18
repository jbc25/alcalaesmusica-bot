import requests
from bot.utils.constants import URL_BASE
from bot.models.news import News


def get_news_api():
    response = requests.get(f'{URL_BASE}/api/v1/blog/')
    if response.status_code == 200:
        news_list = News.parse(response.text)
        return news_list
    else:
        raise Exception(f'API error: {response.status_code}\n{response.text}')
