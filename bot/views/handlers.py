import telegram
import requests
import json
from bot.models.event import Event
from bot.models.tag import Tag
from .events import *
from datetime import datetime, timedelta
from bot.utils.keyboards_markup import *
from bot.models.preference import Preference
from bot.utils.preference_keys import *


def start(update, context):
    text = "<b>¡Bienvenid@!</b>\nA partir de ahora será muy fácil enterarte de los eventos musicales de la ciudad. " \
           "Es muy fácil comunicarte conmigo, escríbeme /eventos y te prepararé en un instante la lista de todos " \
           "los eventos musicales programados en adelante, podrás filtrar por estilos de música.\n\nSi solo " \
           "te interesan los del siguiente fin de semana mándame un /finde.\n\nY si quieres que te avise automáticamente" \
           "cuando haya nuevos conciertos que te interesen, mandame /avisos y elige los estilos que te gusten. " \
           "Yo estaré siempre atento para avisarte y que no se te pase ninguno!"

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

    prepare_text_and_send(events_finde, 'Eventos del próximo fin de semana', context.bot, update.effective_chat.id,
                          no_events_text='No hay eventos para el fin de semana')


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
        context.bot.answer_callback_query(callback_query_id=query.id)  # , text=answer_text (for banner message)
        events_filtered = filter_events(tag_id)
        filter_text = f'Filtrando por {answer_text.upper()}\nPulsa /eventos para mostrar todos'
        text = prepare_text(events_filtered, filter_text, no_events_text=f'No hay eventos para la categoría: {answer_text.upper()}')
        context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=query.message.message_id,
                                      text=text[0], parse_mode="HTML", disable_web_page_preview=True, reply_markup=tags_keyboard())


def notices(update, context):
    text = "🚧 ¡Ei! Esto todavía está en construcción. 🚧"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode="HTML",
                             reply_markup=telegram.ReplyKeyboardRemove())


def remove_cache(update, context):
    Preference.remove(PREF_EVENTS_CACHE)
    Preference.remove(PREF_CACHE_TIMESTAMP)
    context.bot.send_message(chat_id=update.effective_chat.id, text='Caché borrada', parse_mode="HTML",
                             reply_markup=telegram.ReplyKeyboardRemove())


def send_dev_chat_message(context, message):
    context.bot.send_message(chat_id=15480516, text=message)
