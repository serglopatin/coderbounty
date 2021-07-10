# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0006_auto_20151115_0005'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='delta',
            name='user',
        ),
        migrations.DeleteModel(
            name='Delta',
        ),
        migrations.AlterUniqueTogether(
            name='userservice',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='userservice',
            name='service',
        ),
        migrations.RemoveField(
            model_name='userservice',
            name='user',
        ),
        migrations.DeleteModel(
            name='UserService',
        ),
        migrations.RemoveField(
            model_name='watcher',
            name='issue',
        ),
        migrations.RemoveField(
            model_name='watcher',
            name='user',
        ),
        migrations.DeleteModel(
            name='Watcher',
        ),
        migrations.RemoveField(
            model_name='xp',
            name='user',
        ),
        migrations.DeleteModel(
            name='XP',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='coins',
        ),
    ]
