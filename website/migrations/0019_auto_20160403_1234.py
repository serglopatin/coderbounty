# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0018_auto_20151211_2116'),
    ]

    operations = [
        migrations.AddField(
            model_name='solution',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2016, 4, 3, 16, 34, 19, 846000, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='comment',
            name='service_comment_id',
            field=models.IntegerField(unique=True),
        ),
        migrations.AlterField(
            model_name='issue',
            name='status',
            field=models.CharField(default=b'open', max_length=255, choices=[(b'open', b'open'), (b'in review', b'in review'), (b'paid', b'paid'), (b'closed', b'closed')]),
        ),
        migrations.AlterField(
            model_name='solution',
            name='status',
            field=models.CharField(default=b'open', max_length=250, choices=[(b'open', b'open'), (b'merged', b'merged'), (b'closed', b'closed')]),
        ),
        migrations.AlterField(
            model_name='solution',
            name='url',
            field=models.URLField(help_text=b'Pull Request URL'),
        ),
    ]
