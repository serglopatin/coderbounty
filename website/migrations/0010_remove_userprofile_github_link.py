# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0009_auto_20151117_1000'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='github_link',
        ),
    ]
