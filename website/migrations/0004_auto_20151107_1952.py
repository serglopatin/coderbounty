# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0003_auto_20151021_1455"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="issue",
            options={"ordering": ["-created"]},
        ),
        migrations.AlterField(
            model_name="bounty",
            name="user",
            field=models.ForeignKey(
                to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="issue",
            name="language",
            field=models.CharField(
                blank=True,
                max_length=255,
                choices=[
                    (b"Java", b"Java"),
                    (b"C", b"C"),
                    (b"C++", b"C++"),
                    (b"PHP", b"PHP"),
                    (b"VB", b"VB"),
                    (b"Python", b"Python"),
                    (b"C#", b"C#"),
                    (b"JavaScript", b"JavaScript"),
                    (b"Perl", b"Perl"),
                    (b"Ruby", b"Ruby"),
                    (b"HTML", b"HTML"),
                ],
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="issue",
            name="notified_user",
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="issue",
            name="number",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="issue",
            name="service",
            field=models.ForeignKey(
                related_name="+",
                default=None,
                to="website.Service",
                on_delete=models.CASCADE,
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="user",
            field=models.OneToOneField(
                related_name="userprofile",
                to=settings.AUTH_USER_MODEL,
                on_delete=models.CASCADE,
            ),
            preserve_default=True,
        ),
    ]
