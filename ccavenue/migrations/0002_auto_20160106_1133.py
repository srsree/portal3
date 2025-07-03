# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ccavenue', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Address',
        ),
        migrations.AddField(
            model_name='subscription',
            name='address',
            field=models.CharField(max_length=500, null=True, verbose_name=b'Address', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='subscription',
            name='city',
            field=models.CharField(max_length=500, null=True, verbose_name=b'City', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='subscription',
            name='country',
            field=models.CharField(max_length=500, null=True, verbose_name=b'Country', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='subscription',
            name='email',
            field=models.CharField(max_length=200, null=True, verbose_name=b'Email', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='subscription',
            name='name',
            field=models.CharField(default='test', max_length=200, verbose_name=b'Customer name'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='subscription',
            name='phone',
            field=models.CharField(max_length=200, null=True, verbose_name=b'Phone', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='subscription',
            name='pincode',
            field=models.CharField(max_length=500, null=True, verbose_name=b'Zip/Pin code', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='subscription',
            name='profession',
            field=models.CharField(max_length=200, null=True, verbose_name=b'Profession', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='subscription',
            name='state',
            field=models.CharField(max_length=500, null=True, verbose_name=b'State', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='subscription',
            name='year',
            field=models.CharField(max_length=200, null=True, verbose_name=b'Years of subscription', blank=True),
            preserve_default=True,
        ),
    ]
