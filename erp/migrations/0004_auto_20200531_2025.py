# Generated by Django 3.0.6 on 2020-05-31 23:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0003_auto_20200523_1610'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='descripcion',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
