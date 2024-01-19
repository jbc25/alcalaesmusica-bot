import time

from django.core.management.base import BaseCommand

from bot.dev_config import *
from bot.models.user_chat import UserChat
from bot.views.events import *


class Command(BaseCommand):
    help = 'Notify new events to users (for cron jobs)'

    # def add_arguments(self, parser):
    #     parser.add_argument('jsonfile', type=str, help='Indicates the JSON file to export entities')

    def handle(self, *args, **options):

        from bot.apps import bot

        events = get_events()
        if not events:
            return

        if developing:
            user_chats = UserChat.objects.filter(id_chat=dev_chat_id)
        else:
            user_chats = UserChat.objects.all()

        for user_chat in user_chats:
            time.sleep(0.3)
            chat_id = user_chat.id_chat
            events_notified = EventNotified.objects.get(pk=chat_id)
            ids_events_notified = json.loads(events_notified.ids_events)

            events_notify = []

            has_subscriptions = TagSubscription.objects.filter(id_chat=chat_id)

            for event in events:
                # If no subscriptions, notify all
                if not has_subscriptions:
                    if event.id not in ids_events_notified:
                        events_notify.append(event)
                        ids_events_notified.append(event.id)
                else:
                    if len(event.bands) == 0:
                        # Don't know what band and tag is so just notify it
                        if event.id not in ids_events_notified:
                            events_notify.append(event)
                            ids_events_notified.append(event.id)
                    else:
                        for band in event.bands:
                            tag_subscription = TagSubscription.objects.filter(id_chat=chat_id, tag__id=band.tag_id).first()
                            if not tag_subscription or (tag_subscription and tag_subscription.subscribed) or band.tag_id == -1:
                                if event.id not in ids_events_notified:
                                    events_notify.append(event)
                                    ids_events_notified.append(event.id)

            print(f'Notifying {len(events_notify)} events')

            if events_notify:

                try:
                    prepare_text_and_send(events_notify, '<b>¡Nuevos conciertos!</b>', bot, chat_id)
                    events_notified.ids_events = json.dumps(ids_events_notified)
                    events_notified.save()
                    user_chat.is_active = True
                except telegram.error.Unauthorized:
                    user_chat.is_active = False

                user_chat.save()

