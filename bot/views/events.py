import requests
import telegram
from bot.models.event import Event


def get_events():
    response = requests.get(f'https://alcalaesmusica.org/api/v1/events/?limit=250&offset=250')
    if response.status_code == 200:
        return Event.parse_events(response.text)
    else:
        raise Exception(f'API error: {response.status_code}\n{response.text}')


def get_reply_keyboard_markup():
    return telegram.ReplyKeyboardRemove()
    # custom_keyboard = [[
    #         telegram.KeyboardButton(text='/eventos'),
    #         telegram.KeyboardButton(text='/finde'),
    # ]]
    # reply_keyboard_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=False, resize_keyboard=True)
    # return reply_keyboard_markup


def prepare_text_and_send(events, initial_text, bot, chat_id, reply_markup=telegram.ReplyKeyboardRemove()):
    if not events:
        bot.send_message(chat_id=chat_id, text='No hay eventos próximamente', parse_mode="HTML",
                         disable_web_page_preview=True,
                         reply_markup=reply_markup)
        return

    text = initial_text + "\n\n"

    for event in events:
        text += '<b><a href="%s">%s</a></b>' % (event.link, event.title)
        # text += '\n<i>➪ %s</i>' % event.get_type_names() if len(event.event_types.all()) > 0 else ''
        text += '\n📅 %s: ' % event.get_date_human_format()
        text += '\n🕑 %s' % event.get_time_human_format()
        text += '\n\n'

    bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML",
                     disable_web_page_preview=True,
                     reply_markup=reply_markup)
