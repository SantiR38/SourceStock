# Generated by Django 3.0.6 on 2020-06-25 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0009_auto_20200613_2307'),
    ]

    operations = [
        migrations.AddField(
            model_name='detalleentrada',
            name='porcentaje_ganancia',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=10),
            preserve_default=False,
        ),
    ]