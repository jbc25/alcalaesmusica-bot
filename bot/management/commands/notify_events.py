import json

from django.core.management.base import BaseCommand

from bot.models.tag import Tag
from bot.models.user_chat import UserChat
from bot.models.event_notices import *
from bot.views.events import *
import json


class Command(BaseCommand):
    help = 'Notify new events to users (for cron jobs)'

    # def add_arguments(self, parser):
    #     parser.add_argument('jsonfile', type=str, help='Indicates the JSON file to export entities')

    def handle(self, *args, **options):

        from bot.apps import bot

        events = get_events()
        if not events:
            return

        user_chats = UserChat.objects.all()

        for user_chat in user_chats:
            chat_id = user_chat.id_chat
            events_notified = EventNotified.objects.get(pk=chat_id)
            ids_events_notified = json.loads(events_notified.ids_events)

            events_notify = []

            has_subscriptions = TagNotice.objects.filter(id_chat=chat_id)

            for event in events:
                # If no subscriptions, notify all
                if not has_subscriptions:
                    if event.id not in ids_events_notified:
                        events_notify.append(event)
                        ids_events_notified.append(event.id)
                else:
                    for band in event.bands:
                        tag_notice = TagNotice.objects.filter(id_chat=chat_id, tag__id=band.tag_id).first()
                        if tag_notice and tag_notice.subscribed:
                            if event.id not in ids_events_notified:
                                events_notify.append(event)
                                ids_events_notified.append(event.id)

            print(f'Notifying {len(events_notify)} events')

            if events_notify:

                prepare_text_and_send(events_notify, '¡Nuevos conciertos!', bot, chat_id)

                events_notified.ids_events = json.dumps(ids_events_notified)
                events_notified.save()
