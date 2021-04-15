# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0007_auto_20151116_0614'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='github_link',
            field=models.CharField(help_text=b'https://github.com/username/', max_length=100, null=True, verbose_name=b'GitHub account', blank=True),
            preserve_default=True,
        ),
    ]
