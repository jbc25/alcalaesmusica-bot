# Generated by Django 3.2.11 on 2022-11-10 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0008_analytic'),
    ]

    operations = [
        migrations.AddField(
            model_name='userchat',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]