# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.conf import settings
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("website", "0017_comment"),
    ]

    operations = [
        migrations.RenameField(
            model_name="solution",
            old_name="submitted_at",
            new_name="created",
        ),
        migrations.RenameField(
            model_name="solution",
            old_name="pr_link",
            new_name="url",
        ),
        migrations.RemoveField(
            model_name="solution",
            name="submitted_by",
        ),
        migrations.AddField(
            model_name="solution",
            name="user",
            field=models.ForeignKey(
                default=1, to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
            ),
            preserve_default=False,
        ),
    ]
