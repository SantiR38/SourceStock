# Generated by Django 3.1 on 2020-10-27 23:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0041_auto_20201026_0228'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='en_dolar',
            field=models.BooleanField(default=False, null=True),
        ),
    ]