# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-18 20:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nc', '0060_auto_20181018_1754'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='created',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='comment',
            name='created',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]
