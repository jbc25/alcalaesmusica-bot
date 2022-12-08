# Generated by Django 3.2.11 on 2022-05-31 22:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0007_rename_tagnotice_tagsubscription'),
    ]

    operations = [
        migrations.CreateModel(
            name='Analytic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=20)),
                ('name', models.CharField(max_length=100)),
                ('data_text', models.CharField(max_length=100, null=True)),
                ('data_id', models.BigIntegerField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
