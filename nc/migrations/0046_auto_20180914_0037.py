# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-09-14 00:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nc', '0045_asset_trusters'),
    ]

    operations = [
        migrations.AddField(
            model_name='portfolio',
            name='usd_value',
            field=models.FloatField(default=-1.0),
        ),
        migrations.AddField(
            model_name='portfolio',
            name='xlm_value',
            field=models.FloatField(default=-1.0),
        ),
    ]