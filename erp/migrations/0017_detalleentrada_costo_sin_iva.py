# Generated by Django 3.0.6 on 2020-07-11 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0016_auto_20200707_2314'),
    ]

    operations = [
        migrations.AddField(
            model_name='detalleentrada',
            name='costo_sin_iva',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]
