# Generated by Django 3.1.1 on 2020-11-03 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Empresa',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200, verbose_name='Nombre')),
                ('razon_social', models.CharField(blank=True, max_length=200, null=True, verbose_name='Razon Social')),
                ('num_registro', models.CharField(max_length=12, unique=True, verbose_name='Registro')),
                ('nit', models.CharField(blank=True, max_length=17, null=True, unique=True, verbose_name='NIT')),
                ('direccion', models.CharField(blank=True, max_length=50, null=True, verbose_name='Direccion')),
                ('giro1', models.CharField(blank=True, max_length=200, null=True, verbose_name='Actividad Economica 1')),
                ('giro2', models.CharField(blank=True, max_length=200, null=True, verbose_name='Actividad Economica 2')),
                ('giro3', models.CharField(blank=True, max_length=200, null=True, verbose_name='Actividad Economica 3')),
                ('telefono', models.CharField(blank=True, max_length=50, null=True, verbose_name='Telefono')),
                ('contabilidad', models.BooleanField(default=False, verbose_name='Contabilidad')),
                ('creado', models.DateTimeField(auto_now_add=True, verbose_name='Creado')),
            ],
            options={
                'verbose_name': 'Empresa',
                'verbose_name_plural': 'Empresas',
            },
        ),
    ]
