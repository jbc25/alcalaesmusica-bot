# Generated by Django 3.2.11 on 2022-04-16 21:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0003_auto_20220415_0816'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tagnotice',
            name='tag',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='bot.tag'),
        ),
    ]
