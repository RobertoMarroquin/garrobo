# Generated by Django 3.1.1 on 2020-12-02 20:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('iva', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facturacm',
            name='empresa',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='iva.empresa'),
        ),
    ]