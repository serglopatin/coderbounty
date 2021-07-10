# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0015_solution_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='taker',
            old_name='issueTaken',
            new_name='created',
        ),
        migrations.RemoveField(
            model_name='taker',
            name='is_taken',
        ),
        migrations.RemoveField(
            model_name='taker',
            name='issueEnd',
        ),
        migrations.RemoveField(
            model_name='taker',
            name='status',
        ),
        migrations.AlterField(
            model_name='issue',
            name='language',
            field=models.CharField(blank=True, max_length=255, choices=[(b'C#', b'C#'), (b'C', b'C'), (b'C++', b'C++'), (b'CSS', b'CSS'), (b'Erlang', b'Erlang'), (b'Haskell', b'Haskell'), (b'HTML', b'HTML'), (b'Java', b'Java'), (b'JavaScript', b'JavaScript'), (b'NodeJS', b'NodeJS'), (b'Perl', b'Perl'), (b'PHP', b'PHP'), (b'Python', b'Python'), (b'Ruby', b'Ruby'), (b'Scala', b'Scala'), (b'Shell', b'Shell'), (b'VB', b'VB')]),
        ),
    ]
