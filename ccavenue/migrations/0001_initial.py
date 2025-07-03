# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('addresstype', models.CharField(max_length=b'200', verbose_name=b'Address type', choices=[(b'Billing', b'Billing'), (b'Delivery', b'Delivery')])),
                ('name', models.CharField(max_length=200, verbose_name=b'Customer name')),
                ('email', models.CharField(max_length=200, null=True, verbose_name=b'Email', blank=True)),
                ('phone', models.CharField(max_length=200, null=True, verbose_name=b'Phone', blank=True)),
                ('address', models.CharField(max_length=500, null=True, verbose_name=b'Address', blank=True)),
                ('city', models.CharField(max_length=500, null=True, verbose_name=b'City', blank=True)),
                ('state', models.CharField(max_length=500, null=True, verbose_name=b'State', blank=True)),
                ('country', models.CharField(max_length=500, null=True, verbose_name=b'Country', blank=True)),
                ('pincode', models.CharField(max_length=500, null=True, verbose_name=b'Zip/Pin code', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('amount', models.CharField(max_length=200, verbose_name=b'Amount*')),
                ('orderid', models.CharField(max_length=200, verbose_name=b'Unique ID sent by us')),
                ('status', models.CharField(max_length=200, verbose_name=b'Status of Transaction', choices=[(b'Pending', b'Pending'), (b'Success', b'Success'), (b'Failure', b'Failure'), (b'Aborted', b'Aborted'), (b'Invalid', b'Invalid')])),
                ('message', models.CharField(max_length=500, null=True, verbose_name=b'Failure Message', blank=True)),
                ('bankref', models.CharField(max_length=500, null=True, verbose_name=b'Bank Reference Number', blank=True)),
                ('txnid', models.CharField(max_length=500, null=True, verbose_name=b'Transaction Number', blank=True)),
                ('payment_mode', models.CharField(max_length=500, null=True, verbose_name=b'mode of Payment', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
