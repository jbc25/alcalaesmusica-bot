import telegram
from bot.models.tag import Tag
from bot.models.event_notices import *
import json


class InlineButton:
    def __init__(self, name, type, data=None):
        self.name = name
        self.type = type
        self.data = data

    ACCESS_FILTER_TAGS = "access_filter_tags"
    FILTER_TAG = "filter_tag"
    NOTICES_TAG = "notices_tag"


def create_inline_keyboard(items, buttons_per_row):
    inline_keyboard = [[]]

    for index, item in enumerate(items):
        current_row = int(index / buttons_per_row)
        if not inline_keyboard[current_row]:
            inline_keyboard.append([])

        callback_data = json.dumps({'type': item.type, 'data': item.data})

        inline_keyboard[current_row].append(
            telegram.InlineKeyboardButton(text=item.name, callback_data=callback_data))

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
        tag_notices_active = TagNotice.objects.filter(id_chat=chat_id, tag__id=tag.id).first()
        if tag_notices_active is not None:
            print(tag_notices_active)
            tag.name = ("✅ " if tag_notices_active.subscribed else "") + tag.name

    items = list(map(lambda tag: InlineButton(tag.name, InlineButton.NOTICES_TAG, data=tag.id), tags))
    return create_inline_keyboard(items, 3)

