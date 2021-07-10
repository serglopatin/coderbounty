# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0002_auto_20150413_0435"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bounty",
            name="ends",
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="bounty",
            name="user",
            field=models.ForeignKey(
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="issue",
            name="number",
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="issue",
            name="service",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="website.Service",
                null=True,
                on_delete=models.CASCADE,
            ),
            preserve_default=True,
        ),
    ]
