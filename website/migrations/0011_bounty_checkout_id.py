# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0010_remove_userprofile_github_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='bounty',
            name='checkout_id',
            field=models.IntegerField(null=True),
        ),
    ]
