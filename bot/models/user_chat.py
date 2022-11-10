
from django.db import models


class UserChat(models.Model):

    id_chat = models.BigIntegerField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.id_chat}, admin: {self.is_admin}, active: {self.is_active}, created: {self.created_at.strftime("%Y-%m-%d %H:%M:%S")}'
