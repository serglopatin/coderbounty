# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0014_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='solution',
            name='status',
            field=models.CharField(default=b'in review', max_length=250, choices=[(b'in review', b'In review'), (b'Merged or accepted', b'Merged or accepted'), (b'Requested for revision', b'Requested for revision')]),
        ),
    ]
