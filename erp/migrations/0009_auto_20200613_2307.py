# Generated by Django 3.0.6 on 2020-06-14 02:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0008_detalleentrada_detalleperdida_detalleventa'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entrada',
            name='fecha',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='perdida',
            name='fecha',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='venta',
            name='fecha',
            field=models.DateField(),
        ),
    ]
