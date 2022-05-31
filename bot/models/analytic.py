from django.db import models


class Analytic(models.Model):
    type = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    data_text = models.CharField(max_length=100, null=True)
    data_id = models.BigIntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    TYPE_COMMAND = "command"
    TYPE_INLINE_BUTTON = "inline_button"
    TYPE_FREE_TEXT = "free_text"

    @staticmethod
    def save_analytic(type, name, data_text=None, data_id=None):
        analytic = Analytic(type=type, name=name, data_text=data_text, data_id=data_id)
        analytic.save()


    def __str__(self):
        return f'type={self.type}, name={self.name}'
