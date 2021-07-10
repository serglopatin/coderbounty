# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0008_userprofile_github_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='payment_service',
            field=models.CharField(blank=True, max_length=255, null=True, choices=[(b'wepay', 'WePay')]),
            preserve_default=True,
        ),
    ]
