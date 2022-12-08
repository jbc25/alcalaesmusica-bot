# Generated by Django 3.2.11 on 2022-04-14 16:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=300)),
                ('description', models.TextField(blank=True)),
                ('poster', models.CharField(max_length=300)),
                ('link', models.CharField(max_length=100)),
                ('day', models.CharField(max_length=30)),
                ('time', models.CharField(max_length=30)),
                ('datetime', models.CharField(max_length=30)),
                ('duration', models.FloatField(blank=True, null=True)),
                ('price', models.FloatField(blank=True, null=True)),
                ('price_preorder', models.FloatField(blank=True, null=True)),
                ('ticket_link', models.CharField(max_length=200)),
                ('venue_id', models.BigIntegerField(blank=True, null=True)),
                ('venue_name', models.CharField(blank=True, max_length=200, null=True)),
                ('venue_address', models.CharField(blank=True, max_length=200, null=True)),
                ('venue_name_ext', models.CharField(blank=True, max_length=200, null=True)),
                ('venue_address_ext', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EventNotified',
            fields=[
                ('id_chat', models.BigIntegerField(primary_key=True, serialize=False)),
                ('ids_events', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Preference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.TextField(unique=True)),
                ('str_value', models.TextField(null=True)),
                ('int_value', models.IntegerField(null=True)),
                ('bool_value', models.BooleanField(null=True)),
                ('float_value', models.FloatField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
                ('color', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='TagNotice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_chat', models.BigIntegerField(blank=True)),
                ('subscribed', models.BooleanField()),
                ('tag', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='bot.tag')),
            ],
        ),
    ]