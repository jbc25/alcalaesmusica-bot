import requests
import telegram
from bot.models.event import Event
from bot.models.preference import Preference
from datetime import datetime, timedelta
from bot.utils.preference_keys import *

DATETIME_FORMAT_API = '%Y-%m-%d %H:%M:%S'


def get_events():

    cache_timestamp = Preference.get(PREF_CACHE_TIMESTAMP, '2022-04-13 06:00:00')
    cache_datetime = datetime.strptime(cache_timestamp, DATETIME_FORMAT_API)
    now_minus_5_mins = datetime.now() - timedelta(minutes=5)
    if cache_datetime > now_minus_5_mins:
        # save 5 mins of cache
        return get_events_cache()
    else:
        return get_events_api()


def get_events_cache():
    cache_json = Preference.get(PREF_EVENTS_CACHE)
    if not cache_json:
        return get_events_api()

    events = Event.parse_events(cache_json)
    print(f'getting events from cache. len: {len(events)}')
    return events


def get_events_api():
    response = requests.get(f'https://alcalaesmusica.org/api/v1/upcoming_events/')
    if response.status_code == 200:
        events = Event.parse_events(response.text)
        Preference.set(PREF_EVENTS_CACHE, response.text)
        Preference.set(PREF_CACHE_TIMESTAMP, datetime.now().strftime(DATETIME_FORMAT_API))
        print(f'getting events from api. len: {len(events)}')
        return events
    else:
        raise Exception(f'API error: {response.status_code}\n{response.text}')


def filter_events(tag_id):
    events = get_events()
    filtered = []
    for event in events:
        for band in event.bands:
            print(type(band.tag_id))
            print(type(tag_id))
            if int(band.tag_id) == tag_id:
                filtered.append(event)
    return filtered


def prepare_text(events, initial_text, no_events_text='No hay eventos próximamente'):
    if not events:
        return [no_events_text]

    events_limit = 30   # more than this number could result in a "Message too long" error
    text_slices = []

    text = initial_text + "\n\n"

    for i, event in enumerate(events):
        text += f'<b><a href="%s">%s</a></b>' % (event.link, event.title)
        # text += '\n<i>➪ %s</i>' % event.get_type_names() if len(event.event_types.all()) > 0 else ''
        text += '\n📅 %s: ' % event.get_date_human_format()
        text += '\n🕑 %s' % event.get_time_human_format()
        for band in event.bands:
            text += '\n🎸 %s' % f'{band.name} ({band.tag_name})'
        text += '\n📍 %s' % event.get_place()

        text += '\n\n'

        if i > 0 and i % events_limit == 0:
            text_slices.append(text)
            text = ""

    text_slices.append(text)
    return text_slices


def prepare_text_and_send(events, initial_text, bot, chat_id, reply_markup=telegram.ReplyKeyboardRemove()):

    text_slices = prepare_text(events, initial_text)
    for i, text in enumerate(text_slices):
        bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML",
                         disable_web_page_preview=True,
                         reply_markup=reply_markup if i == len(text_slices)-1 else telegram.ReplyKeyboardRemove())
