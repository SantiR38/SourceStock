# Generated by Django 3.0.6 on 2020-05-23 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0002_auto_20200523_1601'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='stock',
            field=models.IntegerField(verbose_name='Cantidad'),
        ),
    ]