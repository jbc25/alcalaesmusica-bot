from django.db import models


class Preference(models.Model):
    key = models.TextField(unique=True, null=False, blank=False)
    str_value = models.TextField(null=True)
    int_value = models.IntegerField(null=True)
    bool_value = models.BooleanField(null=True)
    float_value = models.FloatField(null=True)

    @staticmethod
    def set(key, value):
        pref = Preference.objects.filter(key=key).first()
        if not pref:
            pref = Preference(key=key)

        if isinstance(value, str):
            pref.str_value = value
        elif isinstance(value, int):
            pref.int_value = value
        elif isinstance(value, bool):
            pref.bool_value = value
        elif isinstance(value, float):
            pref.float_value = value
        else:
            raise Exception('value type not valid: ' + str(value))

        pref.save()

    @staticmethod
    def get(key, default_value=None):

        pref = Preference.objects.filter(key=key).first()

        if not pref:
            return default_value

        if pref.str_value:
            return pref.str_value
        elif pref.int_value:
            return pref.int_value
        elif pref.bool_value:
            return pref.bool_value
        elif pref.float_value:
            return pref.float_value
        else:
            return default_value

    @staticmethod
    def remove(key):
        pref = Preference.objects.filter(key=key).first()
        if pref:
            pref.delete()

    def __str__(self):
        return f'key={self.key}, value={self.get(self.key)}'
