# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mcms.thumbs
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('mcms', '0004_aboutus'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='photofeatureimage',
            name='photofeature_ptr',
        ),
        migrations.AddField(
            model_name='photofeatureimage',
            name='active',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='photofeatureimage',
            name='created_on',
            field=models.DateTimeField(default='1', auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='photofeatureimage',
            name='description',
            field=ckeditor.fields.RichTextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='photofeatureimage',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, default='1', serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='photofeatureimage',
            name='image',
            field=mcms.thumbs.ImageWithThumbsField(null=True, upload_to=b'static/%Y/%m/%d', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='photofeatureimage',
            name='modified_on',
            field=models.DateTimeField(default='1', auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='photofeatureimage',
            name='name',
            field=models.CharField(default='name', max_length=200, verbose_name=b'Name*'),
            preserve_default=False,
        ),
    ]
