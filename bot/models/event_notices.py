
from django.db import models
from bot.models.tag import Tag
import json


class TagSubscription(models.Model):
    id_chat = models.BigIntegerField(blank=True) # In private chats user_id is the same as chat_id: https://stackoverflow.com/a/59750179/1365440
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, null=True)
    subscribed = models.BooleanField()

    def __str__(self):
        return f'id_chat: {self.id_chat}, tag: {self.tag.name}, subscribed: {self.subscribed} '


class EventNotified(models.Model):
    id_chat = models.BigIntegerField(primary_key=True)
    ids_events = models.TextField(blank=False, default='[]')

    def add_id_event(self, id):
        list_ids_events = json.loads(self.ids_events)
        list_ids_events.append(id)
        self.ids_events = json.dumps(list_ids_events)

    def __str__(self):
        list_ids_events = json.loads(self.ids_events)
        return f'id_chat: {self.id_chat}, events notified number: {len(list_ids_events)}. ' \
               f'Ids: {",".join([str(id) for id in list_ids_events])}'
