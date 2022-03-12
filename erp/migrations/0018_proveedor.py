# Generated by Django 3.0.6 on 2020-08-04 23:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0017_detalleentrada_costo_sin_iva'),
    ]

    operations = [
        migrations.CreateModel(
            name='Proveedor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('condicion_iva', models.CharField(max_length=25)),
                ('cuit', models.CharField(max_length=15, null=True)),
                ('direccion', models.CharField(max_length=50, null=True)),
                ('telefono', models.CharField(max_length=30, null=True)),
                ('email', models.EmailField(max_length=254, null=True)),
            ],
        ),
    ]