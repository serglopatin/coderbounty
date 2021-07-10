# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0011_bounty_checkout_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="Solution",
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
                ("submitted_at", models.DateTimeField(auto_now_add=True)),
                ("pr_link", models.URLField(help_text=b"Pull Request Link ")),
                (
                    "issue",
                    models.ForeignKey(to="website.Issue", on_delete=models.CASCADE),
                ),
                (
                    "submitted_by",
                    models.ForeignKey(
                        to="website.UserProfile", on_delete=models.CASCADE
                    ),
                ),
            ],
        ),
    ]
