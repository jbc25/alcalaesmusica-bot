
from django.db import models


class Tag(models.Model):

    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=30)
    color = models.CharField(max_length=10)

    def __str__(self):
        return self.name

