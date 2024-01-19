import telegram
from bot.models.event_notices import *
import json
from bot.bot_config import URL_BASE


class InlineButton:
    def __init__(self, name, type, data=None, url=None):
        self.name = name
        self.type = type
        self.data = data
        self.url = url

    ACCESS_FILTER_TAGS = "access_filter_tags"
    FILTER_TAG = "filter_tag"
    NOTICES_TAG = "notices_tag"
    URL_BUTTON = "url_button"
    BAND_INFO = "band_info"
    VENUE_INFO = "venue_info"
    EVENT_INFO = "event_info"
    FEST_EVENTS = "fest_events"
    ADMIN_MESSAGE = "admin_message"


def create_inline_keyboard(items, buttons_per_row):
    inline_keyboard = [[]]

    for index, item in enumerate(items):
        current_row = int(index / buttons_per_row)
        if not inline_keyboard[current_row]:
            inline_keyboard.append([])

        if item.type == InlineButton.URL_BUTTON:
            inline_keyboard_button = telegram.InlineKeyboardButton(text=item.name, url=item.url)
        else:
            callback_data = json.dumps({'type': item.type, 'data': item.data})
            inline_keyboard_button = telegram.InlineKeyboardButton(text=item.name, callback_data=callback_data)

        inline_keyboard[current_row].append(inline_keyboard_button)

    return telegram.InlineKeyboardMarkup(inline_keyboard)


def tags_access_keyboard():
    items = [InlineButton('Filtrar estilos musicales', InlineButton.ACCESS_FILTER_TAGS)]
    return create_inline_keyboard(items, 1)


def tags_keyboard():
    tags = Tag.objects.all()
    items = list(map(lambda tag: InlineButton(tag.name, InlineButton.FILTER_TAG, data=tag.id), tags))
    return create_inline_keyboard(items, 3)


def tags_notices_keyboard(chat_id):
    tags = Tag.objects.all()

    for tag in tags:
        tag_subscriptions_active = TagSubscription.objects.filter(id_chat=chat_id, tag__id=tag.id).first()
        if tag_subscriptions_active:
            print(tag_subscriptions_active)
            tag.name = ("✅ " if tag_subscriptions_active.subscribed else "") + tag.name
        else:
            tag.name = "✅ " + tag.name


    items = list(map(lambda tag: InlineButton(tag.name, InlineButton.NOTICES_TAG, data=tag.id), tags))
    return create_inline_keyboard(items, 3)


def event_info_keyboard(event):
    items = []
    if event.ticket_link:
        items.append(InlineButton('Comprar entradas', InlineButton.URL_BUTTON, url=event.ticket_link))

    for band in event.bands:
        items.append(InlineButton(f'Información de {band.name}', InlineButton.BAND_INFO,
                                  data=str(event.id) + '-' + str(band.id)))

    if event.venue.has_data():
        items.append(InlineButton(f'Información del espacio', InlineButton.VENUE_INFO, data=event.id))

    return create_inline_keyboard(items, 1)


def band_info_keyboard(event, band):
    items = []

    url_band = f'{URL_BASE}/bands/{band.id}'
    items.append(InlineButton('Más información de la banda', InlineButton.URL_BUTTON, url=url_band))

    items.append(InlineButton(f'Información del evento', InlineButton.EVENT_INFO, data=event.id))

    return create_inline_keyboard(items, 1)


def venue_info_keyboard(event):
    items = []

    if event.venue.id:
        url_venue = f'{URL_BASE}/venues/{event.venue.id}'
        items.append(InlineButton('Más información del espacio', InlineButton.URL_BUTTON, url=url_venue))

    if event.venue.lat and event.venue.lng:
        url_venue_map = f'https://maps.google.com/?q={event.venue.lat},{event.venue.lng}'
        items.append(InlineButton('Localizar en el mapa', InlineButton.URL_BUTTON, url=url_venue_map))

    items.append(InlineButton(f'Información del evento', InlineButton.EVENT_INFO, data=event.id))

    return create_inline_keyboard(items, 1)


def fest_keyboard(fest):
    items = [
        InlineButton('Información', InlineButton.URL_BUTTON, url=fest.get_web_link()),
    ]

    if fest.has_events:
        items.append(InlineButton('Conciertos', InlineButton.FEST_EVENTS, data=fest.id))

    return create_inline_keyboard(items, 2)


def custom_fest_keyboard(fest_buttons):
    items = list(map(lambda button: InlineButton(button[0], InlineButton.URL_BUTTON, url=button[1]), fest_buttons))
    return create_inline_keyboard(items, 1)


def admin_message_keyboard():

    items = [
        InlineButton('Enviar', InlineButton.ADMIN_MESSAGE),
    ]

    return create_inline_keyboard(items, 2)


def add_event_keyboard():
    items = [InlineButton('Añadir bolo', InlineButton.URL_BUTTON, url='https://alcalaesmusica.org/events/add/')]
    return create_inline_keyboard(items, 1)
