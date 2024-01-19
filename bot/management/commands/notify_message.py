from django.core.management.base import BaseCommand

from bot.utils.send_msg import send_to_all


class Command(BaseCommand):
    help = 'Notify simple message'

    def add_arguments(self, parser):
        parser.add_argument('message', type=str, help='Message to notify')

    def handle(self, *args, **options):

        message = options['message']
        from bot.apps import bot

        send_to_all(bot, message)

