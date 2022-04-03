import telegram
import requests
import json
from bot.models.event import Event
from bot.models.tag import Tag
from .events import *
from datetime import datetime, timedelta
from bot.utils.keyboards_markup import *


def start(update, context):
    text = "<b>¡Hola!</b> que tal"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode="HTML", reply_markup=telegram.ReplyKeyboardRemove())


def events(update, context):

    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=telegram.ChatAction.TYPING)

    try:
        events = get_events()
        prepare_text_and_send(events, '', context.bot, update.effective_chat.id, tags_access_keyboard())
    except Exception as e:
        send_dev_chat_message(context, str(e))

        import traceback
        print(traceback.format_exc())


def finde(update, context):

    events = get_events()

    events_finde = []
    for event in events:
        friday = 4
        sunday = 6
        today = datetime.now()
        friday_this_week = (today + timedelta(friday - today.weekday())).replace(hour=0, minute=0, second=0)
        sunday_this_week = (today + timedelta(sunday - today.weekday())).replace(hour=23, minute=59, second=59)

        # ini = friday_this_week.strftime("%Y-%m-%d %H:%M:%S")
        # end = sunday_this_week.strftime("%Y-%m-%d %H:%M:%S")
        # print(f'Inicio: {ini}, final {end}, hoy: {today}')

        if event.date_between(friday_this_week, sunday_this_week):
            events_finde.append(event)

    prepare_text_and_send(events_finde, 'Eventos del próximo fin de semana', context.bot, update.effective_chat.id)


def callback_query(update, context):

    query = update.callback_query

    query_data = json.loads(query.data)
    type = query_data['type']

    print(f'INLINE MESSAGE ID: {query.inline_message_id}')

    if type == InlineButton.ACCESS_FILTER_TAGS:
        context.bot.answer_callback_query(callback_query_id=query.id)
        context.bot.edit_message_reply_markup(chat_id=update.effective_chat.id, message_id=query.message.message_id,
                                              reply_markup=tags_keyboard())

    elif type == InlineButton.FILTER_TAG:
        tag_id = query_data['data']
        tag = Tag.objects.get(id=tag_id)
        answer_text = tag.name if tag else 'No se encuentra el Tag'
        context.bot.answer_callback_query(callback_query_id=query.id, text=answer_text)


def send_dev_chat_message(context, message):
    context.bot.send_message(chat_id=15480516, text=message)
