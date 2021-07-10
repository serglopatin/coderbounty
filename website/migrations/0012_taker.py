# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("website", "0011_bounty_checkout_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="Taker",
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
                ("is_taken", models.BooleanField(default=True)),
                (
                    "status",
                    models.CharField(
                        default=b"open",
                        max_length=255,
                        choices=[(b"taken", b"taken"), (b"open", b"open")],
                    ),
                ),
                ("issueTaken", models.DateTimeField(auto_now_add=True)),
                ("issueEnd", models.DateTimeField(null=True, blank=True)),
                (
                    "issue",
                    models.ForeignKey(to="website.Issue", on_delete=models.CASCADE),
                ),
                (
                    "user",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
                    ),
                ),
            ],
        ),
    ]
