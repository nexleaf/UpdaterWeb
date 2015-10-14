# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('uapp', '0002_group_jitter'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='jitter',
            field=models.IntegerField(default=1),
        ),
    ]
