# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='App',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('package', models.CharField(max_length=100)),
                ('ver', models.IntegerField()),
                ('url', models.CharField(max_length=200)),
                ('release', models.CharField(max_length=20)),
                ('action', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20)),
                ('desc', models.TextField(default=b'')),
                ('apps', models.ManyToManyField(to='uapp.App')),
            ],
        ),
        migrations.CreateModel(
            name='Logs',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('imei', models.CharField(max_length=20)),
                ('access', models.DateTimeField()),
                ('packages', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=100)),
                ('imei', models.CharField(max_length=20)),
                ('simid', models.CharField(max_length=40)),
                ('phone', models.CharField(max_length=40)),
                ('group', models.ManyToManyField(to='uapp.Group')),
                ('user_apps', models.ManyToManyField(to='uapp.App')),
            ],
        ),
    ]
