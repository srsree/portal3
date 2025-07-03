# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mcms', '0002_auto_20151228_1648'),
    ]

    operations = [
        migrations.CreateModel(
            name='WriteToUs',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('description', models.TextField(verbose_name=b'Content')),
                ('name', models.CharField(max_length=500, verbose_name=b'Name* ')),
                ('email', models.CharField(max_length=50, verbose_name=b'Email* ')),
                ('location', models.CharField(max_length=100, verbose_name=b'Location*')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
