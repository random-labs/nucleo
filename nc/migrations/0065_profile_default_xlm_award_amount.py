# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-19 13:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nc', '0064_auto_20181018_2204'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='default_xlm_award_amount',
            field=models.FloatField(default=0.0),
        ),
    ]