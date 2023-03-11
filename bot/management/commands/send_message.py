import json

from django.core.management.base import BaseCommand

from bot.models.tag import Tag
from bot.models.user_chat import UserChat
from bot.models.event_notices import *
from bot.views.events import *
from bot.views.news import *
from bot.utils.messages import *
from bot.token import *
from bot.utils.send_msg import send_to_all


class Command(BaseCommand):
    help = 'Notify new news to users (for cron jobs)'

    # def add_arguments(self, parser):
    #     parser.add_argument('jsonfile', type=str, help='Indicates the JSON file to export entities')

    def handle(self, *args, **options):

        from bot.apps import bot

        message = '''
        📣 ¡Este domingo se cierra la inscripción para el #AlcalaSuena 2023!
☝ Si quieres participar con tu banda y todavía no te has inscrito, tienes este fin de semana para hacerlo ¡Date prisa!
🌐 Entra en https://alcalasuena.es/contest/signup/
        '''

        send_to_all(bot, message)

