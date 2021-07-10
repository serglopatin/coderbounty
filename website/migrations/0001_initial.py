# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import datetime


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Bounty",
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
                ("price", models.DecimalField(max_digits=10, decimal_places=0)),
                ("ends", models.DateTimeField()),
                ("created", models.DateTimeField(auto_now_add=True)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Coin",
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
                ("day_of_year", models.PositiveIntegerField(default=0)),
                (
                    "user",
                    models.OneToOneField(
                        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Delta",
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
                ("rank", models.IntegerField(default=0)),
                ("date", models.DateTimeField(default=datetime.datetime.now)),
                (
                    "price",
                    models.DecimalField(default=0, max_digits=10, decimal_places=2),
                ),
                (
                    "user",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL,
                        unique=True,
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Issue",
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
                ("number", models.IntegerField()),
                ("project", models.CharField(max_length=255)),
                ("user", models.CharField(max_length=255, null=True, blank=True)),
                ("image", models.ImageField(upload_to=b"images/projects", blank=True)),
                ("title", models.CharField(max_length=255)),
                ("content", models.TextField(max_length=400)),
                (
                    "language",
                    models.CharField(
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
                        ],
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        default=b"open",
                        max_length=255,
                        choices=[
                            (b"open", b"open"),
                            (b"in review", b"in review"),
                            (b"paid", b"paid"),
                        ],
                    ),
                ),
                (
                    "paid",
                    models.DecimalField(
                        null=True, max_digits=10, decimal_places=0, blank=True
                    ),
                ),
                ("closed_by", models.CharField(max_length=255, null=True, blank=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                ("notified_user", models.BooleanField()),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Service",
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
                ("name", models.CharField(max_length=255)),
                ("domain", models.CharField(max_length=255)),
                ("template", models.CharField(max_length=255)),
                ("regex", models.CharField(max_length=255)),
                (
                    "type",
                    models.CharField(
                        max_length=255,
                        choices=[
                            (b"json", b"json"),
                            (b"xml", b"xml"),
                            (b"http", b"http"),
                        ],
                    ),
                ),
                ("api_url", models.CharField(max_length=255, blank=True)),
                ("link_template", models.CharField(max_length=255, blank=True)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="UserProfile",
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
                (
                    "balance",
                    models.DecimalField(
                        null=True, max_digits=10, decimal_places=2, blank=True
                    ),
                ),
                (
                    "payment_service",
                    models.CharField(max_length=255, null=True, blank=True),
                ),
                (
                    "payment_service_email",
                    models.CharField(
                        default=b"", max_length=255, null=True, blank=True
                    ),
                ),
                ("coins", models.IntegerField(default=0)),
                (
                    "user",
                    models.OneToOneField(
                        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="UserService",
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
                ("username", models.CharField(max_length=255, null=True, blank=True)),
                (
                    "service",
                    models.ForeignKey(
                        related_name="+", to="website.Service", on_delete=models.CASCADE
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Watcher",
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
                ("bounty", models.BooleanField()),
                ("status", models.BooleanField()),
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
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="XP",
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
                ("points", models.IntegerField()),
                ("what_for", models.CharField(max_length=255)),
                (
                    "type",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        choices=[(b"coder", b"coder"), (b"owner", b"owner")],
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name="userservice",
            unique_together=set([("user", "service")]),
        ),
        migrations.AddField(
            model_name="issue",
            name="service",
            field=models.ForeignKey(
                related_name="+", to="website.Service", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="issue",
            name="winner",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="issue",
            unique_together=set([("service", "number", "project")]),
        ),
        migrations.AddField(
            model_name="bounty",
            name="issue",
            field=models.ForeignKey(to="website.Issue", on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="bounty",
            name="user",
            field=models.ForeignKey(
                to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
    ]
