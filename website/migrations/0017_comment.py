# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0016_auto_20151128_2006"),
    ]

    operations = [
        migrations.CreateModel(
            name="Comment",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("content", models.TextField()),
                ("service_comment_id", models.IntegerField()),
                ("username", models.CharField(max_length=255)),
                ("created", models.DateTimeField()),
                ("updated", models.DateTimeField()),
                (
                    "issue",
                    models.ForeignKey(to="website.Issue", on_delete=models.CASCADE),
                ),
            ],
        ),
    ]
