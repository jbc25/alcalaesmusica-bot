# Generated by Django 3.2.11 on 2022-04-13 05:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0003_preference'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='venue_address_ext',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='venue_id',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='venue_name_ext',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='venue_address',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='venue_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]