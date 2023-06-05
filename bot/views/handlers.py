from django.db.models import Count

from bot.models.analytic import Analytic
from bot.models.user_chat import UserChat
from bot.utils.send_msg import send_to_all, send_dev_chat_message
from bot.views.news import *
from .events import *


def start(update, context):

    chat_id = update.effective_chat.id

    user_chat = UserChat.objects.filter(id_chat=chat_id).first()
    if not user_chat:
        user_chat = UserChat(id_chat=chat_id)
    else:
        user_chat.is_active = True

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
        send_dev_chat_message(context.bot, str(e))

        import traceback
        print(traceback.format_exc())

    Analytic.save_analytic(Analytic.TYPE_COMMAND, "conciertos")


def festivals(update, context):

    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=telegram.ChatAction.TYPING)

    try:
        festivals = get_festivals()
        custom_festivals = create_custom_festivals()

        if not festivals and not custom_festivals:
            update.message.reply_text(text='🤷‍♀️ Ahora mismo no hay ciclos o festivales a la vista.'
                                           '\n📢 ¡Te avisaré cuando se organicen!')
            return

        for fest in festivals:
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=fest.get_image_url(), caption=fest.caption(),
                                   parse_mode="HTML", reply_markup=fest_keyboard(fest))

        for custom_fest in custom_festivals:
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=custom_fest['image'],
                                   caption=custom_fest['caption'],
                                   parse_mode="HTML", reply_markup=custom_fest_keyboard(custom_fest['buttons']))

    except Exception as e:
        send_dev_chat_message(context.bot, str(e))

    Analytic.save_analytic(Analytic.TYPE_COMMAND, "festivales")


def finde(update, context):

    events = get_events()

    events_finde = []
    for event in events:
        thursday = 3
        sunday = 6
        today = datetime.now()
        thursday_this_week = (today + timedelta(thursday - today.weekday())).replace(hour=0, minute=0, second=0)
        sunday_this_week = (today + timedelta(sunday - today.weekday())).replace(hour=23, minute=59, second=59)

        # ini = thursday_this_week.strftime("%Y-%m-%d %H:%M:%S")
        # end = sunday_this_week.strftime("%Y-%m-%d %H:%M:%S")
        # print(f'Inicio: {ini}, final {end}, hoy: {today}')

        if event.date_between(thursday_this_week, sunday_this_week):
            events_finde.append(event)

    prepare_text_and_send(events_finde, 'Eventos del próximo fin de semana', context.bot, update.effective_chat.id,
                          no_events_text='No hay eventos para el fin de semana')

    Analytic.save_analytic(Analytic.TYPE_COMMAND, "finde")


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

        Analytic.save_analytic(Analytic.TYPE_INLINE_BUTTON, type)
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

        Analytic.save_analytic(Analytic.TYPE_INLINE_BUTTON, type, data_text=tag.name, data_id=tag.id)
        return

    elif type == InlineButton.NOTICES_TAG:
        tag_id = query_data['data']
        tag = Tag.objects.get(id=tag_id)
        tag_subscription = TagSubscription.objects.filter(id_chat=chat_id, tag__id=tag.id).first()

        if tag_subscription:
            tag_subscription.subscribed = not tag_subscription.subscribed
            tag_subscription.save()
        else:
            tag_subscription = TagSubscription(id_chat=chat_id, tag=tag, subscribed=False)
            tag_subscription.save()

        context.bot.answer_callback_query(callback_query_id=query.id)

        text = "Marca los tipos de música que te interesen y te avisaré cuando se publiquen nuevos conciertos:"
        context.bot.edit_message_text(chat_id=chat_id, message_id=query.message.message_id,
                                      text=text, parse_mode="HTML", reply_markup=tags_notices_keyboard(chat_id))

        Analytic.save_analytic(Analytic.TYPE_INLINE_BUTTON, type, data_text=tag.name, data_id=tag.id)
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

        Analytic.save_analytic(Analytic.TYPE_INLINE_BUTTON, type, data_text=band.name, data_id=band.id)

    elif type == InlineButton.VENUE_INFO:
        id_event = query_data['data']
        event = get_event_by_id(id_event)

        if event.venue.image:
            context.bot.send_photo(chat_id=chat_id, photo=f'{URL_BASE}{event.venue.image}')

        context.bot.send_message(chat_id=chat_id, text=venue_info(event.venue), parse_mode="HTML",
                                 reply_markup=venue_info_keyboard(event))

        Analytic.save_analytic(Analytic.TYPE_INLINE_BUTTON, type, data_text=event.venue.name, data_id=event.venue.id)

    elif type == InlineButton.EVENT_INFO:
        id_event = query_data['data']
        event = get_event_by_id(id_event)
        send_event_info(event, context.bot, chat_id)

        Analytic.save_analytic(Analytic.TYPE_INLINE_BUTTON, type, data_text=event.title, data_id=event.id)

    elif type == InlineButton.FEST_EVENTS:
        id_fest = query_data['data']
        fest_events = get_festival_events(id_fest)
        print(f'id_fest: {id_fest}, len: {len(fest_events)}')
        prepare_text_and_send(fest_events, '', context.bot, update.effective_chat.id,
                                no_events_text='No hay conciertos para este festival')

        Analytic.save_analytic(Analytic.TYPE_INLINE_BUTTON, type, data_id=id_fest)

    elif type == InlineButton.ADMIN_MESSAGE:
        message = query.message.text
        send_to_all(context.bot, message)

    context.bot.answer_callback_query(callback_query_id=query.id)


def notices(update, context):
    if update.effective_chat.type != 'private':
        update.message.reply_text(text='Los avisos funcionan solo en chats privados. Hazlo directamente a través del bot: t.me/alcalaesmusicabot')
        return

    text = "Marca los tipos de música que te interesen y te avisaré cuando se publiquen nuevos conciertos:"

    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text=text, reply_markup=tags_notices_keyboard(chat_id))

    Analytic.save_analytic(Analytic.TYPE_COMMAND, "avisos")


def news(update, context):
    news_list = get_news_api()
    size = len(news_list)
    news_list = news_list[-6:]
    text = '<b>¡Últimas noticias!</b>' + news_list_info(news_list)
    context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode="HTML",
                             disable_web_page_preview=True, reply_markup=telegram.ReplyKeyboardRemove())

    Analytic.save_analytic(Analytic.TYPE_COMMAND, "noticias")


def add(update, context):

    text = "🌐 Pulsa el siguiente botón para abrir la página de añadir evento en la web de Alcalá es Música.\n" \
           "👥 Si es la primera vez, tendrás que entrar con tu usuario.\n\n" \
           "📢 Una vez creado, avisaré en un rato de tu bolo a todo el mundo!"

    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text=text, reply_markup=add_event_keyboard())

    Analytic.save_analytic(Analytic.TYPE_COMMAND, "bolo")

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

    Analytic.save_analytic(Analytic.TYPE_COMMAND, "event_info", data_text=event.title, data_id=event.id)


def any_text(update, context):
    chat_id = update.effective_chat.id
    is_admin = UserChat.objects.get(id_chat=chat_id).is_admin
    if not is_admin:
        text = 'Lo siento, no se lo que me quieres decir 🤔. Estoy dando clases de lenguaje humano pero con tantos ' \
               'conciertos no tengo ni tiempo! 😝\n\nℹ Eso sí, puedo darte toda la información que necesites si me mandas ' \
               'las palabras que entiendo, pulsa el botón "Menú" abajo a la izquierda ↙ y mándame lo que necesites, ' \
               'también entiendo algunos textos dentro de mensajes que empiezan con esta barra / y que puedes pulsar ' \
               'para enviarlo rápidamente.\n\n¡Gracias por comprender a este bot sin cerebro pero con alma rockera! 🤖🎸'
        context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode="HTML",
                             reply_markup=telegram.ReplyKeyboardRemove())
        Analytic.save_analytic(Analytic.TYPE_FREE_TEXT, "text_free", data_text=update.message.text)
    else:
        context.bot.send_message(chat_id=chat_id, text=update.message.text,
                             reply_markup=admin_message_keyboard())


def data(update, context):
    chat_id = update.effective_chat.id
    is_admin = UserChat.objects.get(id_chat=chat_id).is_admin
    if not is_admin:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Esta operación está solo disponible para administradores',
                                 parse_mode="HTML", reply_markup=telegram.ReplyKeyboardRemove())
        return

    user_count = UserChat.objects.all().count()
    user_active_count = UserChat.objects.filter(is_active=True).count()
    text = f'Número de usuarios: <b>{user_count}</b> (activos <b>{user_active_count}</b>)'

    tags_subscriptions = {}
    tags = Tag.objects.all()
    for tag in tags:
        subscriptions = TagSubscription.objects.filter(tag=tag, subscribed=True).count()
        tags_subscriptions[tag.name] = subscriptions

    sorted_tags = sorted(tags_subscriptions.items(), key=lambda item: item[1], reverse=True)

    text += '\n\nRanking de suscripciones a estilos musicales:\n\n'
    for item in sorted_tags:
        text += f'{item[0]}: <b>{item[1]}</b>\n'

    results = TagSubscription.objects.all().values('id_chat').annotate(dcount=Count('id_chat')).order_by()

    users_with_subscription_count = len(results)
    users_with_no_subscription_count = user_count - users_with_subscription_count

    text += f"\n\nUsuarios sin suscripciones: <b>{users_with_no_subscription_count}</b>"

    text += "\n\n<b>Analíticas de uso</b>\n\n"

    analytics_counts = Analytic.objects.all().values('type', 'name').annotate(total=Count('type')).order_by('type')
    for analytic_count in analytics_counts:
        text += f"{analytic_count['type']} -> {analytic_count['name']}: <b>{analytic_count['total']}</b>\n"

    text += '\n<b>Textos libres</b>\n\n'
    free_texts = Analytic.objects.filter(type=Analytic.TYPE_FREE_TEXT)
    for free_text in free_texts:
        text += f'{free_text.data_text}\n'

    context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode="HTML",
                             reply_markup=telegram.ReplyKeyboardRemove())


