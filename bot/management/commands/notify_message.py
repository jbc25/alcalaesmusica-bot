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
    help = 'Notify simple message'

    def add_arguments(self, parser):
        parser.add_argument('message', type=str, help='Message to notify')

    def handle(self, *args, **options):

        message = options['message']
        from bot.apps import bot

        send_to_all(bot, message)

