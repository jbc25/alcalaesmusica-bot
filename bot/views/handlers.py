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
from bot.models.user_chat import UserChat
from bot.utils.messages import *
from bot.views.news import *


def start(update, context):

    chat_id = update.effective_chat.id

    user_chat = UserChat.objects.filter(id_chat=chat_id).first()
    if not user_chat:
        user_chat = UserChat(id_chat=chat_id)
        user_chat.save()

    events_notified = EventNotified.objects.filter(id_chat=chat_id).first()
    if not events_notified:
        events_notified = EventNotified(id_chat=chat_id)
        events_notified.save()

    text = "<b>¡Bienvenid@!</b>\n\nA partir de ahora será muy fácil enterarte de los eventos musicales de la ciudad. " \
           "Es muy fácil comunicarte conmigo, escríbeme /conciertos y te prepararé en un instante la lista de los " \
           "los próximos conciertos, podrás filtrar por estilos de música.\n\n" \
           "También puedes ver los ciclos y festivales escribiendo /festivales\n\n" \
           "Si solo te interesan los conciertos del siguiente fin de semana mándame un /finde.\n\n" \
           "Y si quieres que te avise automáticamente cuando haya nuevos conciertos que te interesen, mandame " \
           "/avisos y elige los estilos que te gusten.\n" \
           "¡Yo estaré siempre atento para avisarte y que no se te pase ninguno!\n\n" \
           "Y por último puedes pulsar /noticias para estar al tanto de las últimas publicaciones.\n" \
           "Aunque tampoco te preocupes mucho por esto porque te enviaré nuevas noticias cuando se publiquen " \
           "sin que tengas que hacer nada.\n\n" \
           "Truco: No hace falta que te aprendas estas instrucciones, las tienes siempre a mano en el botón de " \
           "menú azul abajo a la izquierda 😉"

    context.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=telegram.ReplyKeyboardRemove())


def events(update, context):

    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=telegram.ChatAction.TYPING)

    try:
        events = get_events()
        prepare_text_and_send(events, '', context.bot, update.effective_chat.id, reply_markup=tags_access_keyboard())
    except Exception as e:
        send_dev_chat_message(context, str(e))

        import traceback
        print(traceback.format_exc())


def festivals(update, context):

    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=telegram.ChatAction.TYPING)

    try:
        festivals = get_festivals()
        for fest in festivals:
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=fest.get_image_url(), caption=fest.caption(),
                                   parse_mode="HTML", reply_markup=fest_keyboard(fest))

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

    chat_id = update.effective_chat.id

    print(f'INLINE MESSAGE ID: {query.inline_message_id}')

    if type == InlineButton.ACCESS_FILTER_TAGS:
        context.bot.answer_callback_query(callback_query_id=query.id)
        context.bot.edit_message_reply_markup(chat_id=chat_id, message_id=query.message.message_id,
                                              reply_markup=tags_keyboard())
        return

    elif type == InlineButton.FILTER_TAG:
        tag_id = query_data['data']
        tag = Tag.objects.get(id=tag_id)
        answer_text = tag.name if tag else 'No se encuentra el Tag'
        context.bot.answer_callback_query(callback_query_id=query.id)  # , text=answer_text (for banner message)
        events_filtered = filter_events(tag_id)
        filter_text = f'Filtrando por {answer_text.upper()}\nPulsa /eventos para mostrar todos'
        text = prepare_text(events_filtered, filter_text, no_events_text=f'No hay eventos para la categoría: {answer_text.upper()}')
        context.bot.edit_message_text(chat_id=chat_id, message_id=query.message.message_id,
                                      text=text[0], parse_mode="HTML", disable_web_page_preview=True, reply_markup=tags_keyboard())
        return

    elif type == InlineButton.NOTICES_TAG:
        tag_id = query_data['data']
        tag = Tag.objects.get(id=tag_id)
        tag_notice = TagNotice.objects.filter(id_chat=chat_id, tag__id=tag.id).first()

        if tag_notice:
            tag_notice.subscribed = not tag_notice.subscribed
            tag_notice.save()
        else:
            tag_notice = TagNotice(id_chat=chat_id, tag=tag, subscribed=True)
            tag_notice.save()

        context.bot.answer_callback_query(callback_query_id=query.id)

        text = "Marca los tipos de música que te interesen y te avisaré cuando se publique alguno nuevo:"
        context.bot.edit_message_text(chat_id=chat_id, message_id=query.message.message_id,
                                      text=text, parse_mode="HTML", reply_markup=tags_notices_keyboard(chat_id))
        return

    elif type == InlineButton.BAND_INFO:
        id_event_and_band = query_data['data']
        id_event = int(id_event_and_band.split('-')[0])
        id_band = int(id_event_and_band.split('-')[1])
        event = get_event_by_id(id_event)
        band = next(filter(lambda b: b.id == id_band, event.bands))

        if band.band_image:
            context.bot.send_photo(chat_id=chat_id, photo=f'{URL_BASE}{band.band_image}')

        context.bot.send_message(chat_id=chat_id, text=band_info(band), parse_mode="HTML",
                                 reply_markup=band_info_keyboard(event, band))

    elif type == InlineButton.VENUE_INFO:
        id_event = query_data['data']
        event = get_event_by_id(id_event)

        if event.venue.image:
            context.bot.send_photo(chat_id=chat_id, photo=f'{URL_BASE}{event.venue.image}')

        context.bot.send_message(chat_id=chat_id, text=venue_info(event.venue), parse_mode="HTML",
                                 reply_markup=venue_info_keyboard(event))

    elif type == InlineButton.EVENT_INFO:
        id_event = query_data['data']
        event = get_event_by_id(id_event)
        send_event_info(event, context.bot, chat_id)

    elif type == InlineButton.FEST_EVENTS:
        id_fest = query_data['data']
        fest_events = get_festival_events(id_fest)
        print(f'id_fest: {id_fest}, len: {len(fest_events)}')
        prepare_text_and_send(fest_events, '', context.bot, update.effective_chat.id,
                                no_events_text='No hay conciertos para este festival')

    context.bot.answer_callback_query(callback_query_id=query.id)


def notices(update, context):
    if update.effective_chat.type != 'private':
        update.message.reply_text(text='Los avisos funcionan solo en chats privados. Hazlo directamente a través del bot: t.me/alcalaesmusicabot')
        return

    text = "Marca los tipos de música que te interesen y te avisaré cuando se publiquen nuevos conciertos:"

    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text=text, reply_markup=tags_notices_keyboard(chat_id))


def news(update, context):
    news_list = get_news_api()
    text = '<b>¡Últimas noticias!</b>' + news_list_info(news_list)
    context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode="HTML",
                             disable_web_page_preview=True, reply_markup=telegram.ReplyKeyboardRemove())


def remove_cache(update, context):
    Preference.remove(PREF_EVENTS_CACHE)
    Preference.remove(PREF_CACHE_TIMESTAMP)
    context.bot.send_message(chat_id=update.effective_chat.id, text='Caché borrada', parse_mode="HTML",
                             reply_markup=telegram.ReplyKeyboardRemove())


def event_info_command(update, context):

    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=telegram.ChatAction.TYPING)

    id_event = int(update.message.text.replace('/e', ''))
    event = get_event_by_id(id_event)
    send_event_info(event, context.bot, update.effective_chat.id)


def any_text(update, context):
    text = f'No sé lo que me quieres decir pero por si acaso: ¡<b>{update.message.text}</b> lo serás tu! 😝'
    context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode="HTML",
                             reply_markup=telegram.ReplyKeyboardRemove())


def send_dev_chat_message(context, message):
    context.bot.send_message(chat_id=15480516, text='AemBot dev message:\n' + message)
