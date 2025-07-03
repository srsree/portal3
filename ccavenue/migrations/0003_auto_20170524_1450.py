# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ccavenue', '0002_auto_20160106_1133'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookSubscribers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, null=True, verbose_name=b'Book name', blank=True)),
                ('amount', models.CharField(max_length=200, null=True, verbose_name=b'Amount*', blank=True)),
                ('subscription', models.ForeignKey(to='ccavenue.Subscription')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
#        migrations.AddField(
#            model_name='subscription',
#            name='ptype',
#            field=models.CharField(blank=True, max_length=200, null=True, verbose_name=b'Type of Transaction', choices=[(b'int-1', b'int-1'), (b'int-2', b'int-2'), (b'ind-1', b'ind-1'), (b'ind-2', b'ind-2'), (b'ind-3', b'ind-3'), (b'ind-4', b'ind-4')]),
#            preserve_default=True,
#        ),
#        migrations.AlterField(
#            model_name='subscription',
#            name='country',
#            field=models.ForeignKey(blank=True, to='mcms.Country', null=True),
#            preserve_default=True,
#        ),
    ]
