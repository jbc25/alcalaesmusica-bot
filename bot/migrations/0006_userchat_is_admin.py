# Generated by Django 3.2.11 on 2022-04-21 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0005_auto_20220417_1431'),
    ]

    operations = [
        migrations.AddField(
            model_name='userchat',
            name='is_admin',
            field=models.BooleanField(default=False),
        ),
    ]
