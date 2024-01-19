import requests
from bot.models.event import Event
from bot.models.festival import Festival
from bot.models.preference import Preference
from datetime import datetime, timedelta
from bot.utils.preference_keys import *
from bot.utils.keyboards_markup import *
from bot.bot_config import URL_BASE
from bot.utils.messages import *

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
    response = requests.get(f'{URL_BASE}/api/v1/upcoming_events/')
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
            if int(band.tag_id) == tag_id and not event in filtered:
                filtered.append(event)
    return filtered


def get_festivals():

    response = requests.get(f'{URL_BASE}/api/v1/microsites/')
    if response.status_code == 200:
        festivals = Festival.parse(response.text)
        return festivals
    else:
        raise Exception(f'API error: {response.status_code}\n{response.text}')


def get_festival_events(id_fest):
    events = get_events()
    filtered = []
    for event in events:
        print(f'event microsites len: {len(event.festivals)}')
        for fest in event.festivals:
            if int(fest) == id_fest:
                filtered.append(event)
    return filtered


def create_custom_festivals():
    custom_festivals = []

    # Copy paste this block for each custom festival (not included in "microsites")
    if datetime.now() <= datetime(2023, 6, 4, 23, 59, 59):
        custom_fest = {
            'id': 2,
            'image': 'https://alcalasuena.es/media/news/40124e11-59cb-469e-9315-60967c45bad2.jpg',
            'caption': f'<b>Alcalá Suena</b>\n<i>02/06/2023 - 04/06/2023</i>',
            'buttons': [
                ('Visitar página web', 'https://alcalasuena.es/'),
                ('Descargar app Android', 'https://play.google.com/store/apps/details?id=com.triskelapps.alcalasuena'),
                ('Descargar app iOS', 'https://apps.apple.com/es/app/alcala-suena/id1458551516?l=es&ls=1')
            ]
        }
        custom_festivals.append(custom_fest)
    # -------

    return custom_festivals


def prepare_text(events, initial_text, no_events_text='No hay eventos próximamente'):
    if not events:
        return [no_events_text]

    events_limit = 25   # more than this number could result in a "Message too long" error
    text_slices = []

    text = initial_text + "\n\n"

    for i, event in enumerate(events):
        text += f'<b><a href="%s">%s</a></b>' % (event.link, event.title)
        for band in event.bands:
            text += '\n🎸 %s' % f'{band.name} ({band.tag_name})'
        text += '\n📅 %s' % event.get_date_human_format()
        text += '\n🕑 %s' % event.get_time_human_format()
        text += '\n📍 %s' % event.get_place()
        text += '\nMás info: /e' + str(event.id)

        text += '\n\n'

        if i > 0 and i % events_limit == 0:
            text_slices.append(text)
            text = ""

    if text:
        text_slices.append(text)
    return text_slices


def prepare_text_and_send(events, initial_text, bot, chat_id,
                          no_events_text='No hay eventos próximamente', reply_markup=telegram.ReplyKeyboardRemove()):

    text_slices = prepare_text(events, initial_text, no_events_text)
    for i, text in enumerate(text_slices):

        bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML",
                            disable_web_page_preview=True,
                            reply_markup=reply_markup if i == len(text_slices)-1 else telegram.ReplyKeyboardRemove())


def get_event_by_id(id_event):
    events = get_events()
    event = next(filter(lambda ev: ev.id == id_event, events))
    return event


def send_event_info(event, bot, chat_id):
    if not event:
        bot.send_message(chat_id=chat_id, text='No se ha encontrado información del evento', parse_mode="HTML",
                         reply_markup=telegram.ReplyKeyboardRemove())
    else:

        if event.poster:
            bot.send_photo(chat_id=chat_id, photo=f'{URL_BASE}{event.poster}')

        bot.send_message(chat_id=chat_id, text=event_info(event), parse_mode="HTML",
                         disable_web_page_preview=True,
                         reply_markup=event_info_keyboard(event))
