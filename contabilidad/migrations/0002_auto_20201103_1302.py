# Generated by Django 3.1.1 on 2020-11-03 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contabilidad', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subcuenta',
            name='codigo',
            field=models.CharField(max_length=12, verbose_name='Codigo'),
        ),
    ]
