# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-18 22:04
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nc', '0063_auto_20181018_2140'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='awards_default_account',
            new_name='default_award_account',
        ),
    ]
