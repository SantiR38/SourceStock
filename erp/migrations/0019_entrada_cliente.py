# Generated by Django 3.0.6 on 2020-08-04 23:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0018_proveedor'),
    ]

    operations = [
        migrations.AddField(
            model_name='entrada',
            name='cliente',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='erp.Proveedor'),
        ),
    ]
