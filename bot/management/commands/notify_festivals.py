from django.core.management.base import BaseCommand

from bot.utils.send_msg import send_to_all, send_photo_to_all
from bot.views.events import *


class Command(BaseCommand):
    help = 'Notify new news to users (for cron jobs)'

    # def add_arguments(self, parser):
    #     parser.add_argument('jsonfile', type=str, help='Indicates the JSON file to export entities')

    def handle(self, *args, **options):

        from bot.apps import bot

        festivals = get_festivals()
        custom_festivals = create_custom_festivals()

        if not festivals and not custom_festivals:
            return

        notified_festivals_ids = json.loads(Preference.get(PREF_NOTIFIED_FESTIVALS_IDS, '[]'))
        notified_custom_festivals_ids = json.loads(Preference.get(PREF_NOTIFIED_CUSTOM_FESTIVALS_IDS, '[]'))

        festivals_notify = []
        custom_festivals_notify = []

        for fest in festivals:
            if fest.id not in notified_festivals_ids:
                festivals_notify.append(fest)
                notified_festivals_ids.append(fest.id)

        for custom_fest in custom_festivals:
            if custom_fest['id'] not in notified_custom_festivals_ids:
                custom_festivals_notify.append(custom_fest)
                notified_custom_festivals_ids.append(custom_fest['id'])

        if not festivals_notify and not custom_festivals_notify:
            print('No festivals to notify')
            return

        Preference.set(PREF_NOTIFIED_FESTIVALS_IDS, json.dumps(notified_festivals_ids))
        Preference.set(PREF_NOTIFIED_CUSTOM_FESTIVALS_IDS, json.dumps(notified_custom_festivals_ids))

        initial_text = '<b>¡Nuevos festivales!</b>'

        # This way if there are many festivals to notify at the same time users will have some delays between messages.
        # Many festivals creations at the same time is improbable so this solution is fine at the moment

        for fest in festivals_notify:
            send_photo_to_all(bot, fest.get_image_url(), fest.caption(), fest_keyboard(fest), initial_text)
            initial_text = None

        for custom_fest in custom_festivals_notify:
            send_photo_to_all(bot, custom_fest['image'], custom_fest['caption'],
                              custom_fest_keyboard(custom_fest['buttons']), initial_text)
            initial_text = None

