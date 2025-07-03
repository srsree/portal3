# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mcms.thumbs
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('mcms', '0003_writetous'),
    ]

    operations = [
        migrations.CreateModel(
            name='AboutUs',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=b'200')),
                ('icon', mcms.thumbs.ImageWithThumbsField(null=True, upload_to=b'static/%Y/%m/%d', blank=True)),
                ('description', ckeditor.fields.RichTextField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
