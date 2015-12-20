# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('uapp', '0003_user_jitter'),
    ]

    operations = [
        migrations.AddField(
            model_name='app',
            name='extra_urls',
            field=models.CharField(default=b'', max_length=200),
        ),
    ]
