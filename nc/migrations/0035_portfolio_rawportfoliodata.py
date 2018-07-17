# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-16 15:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nc', '0034_auto_20180710_2209'),
    ]

    operations = [
        migrations.CreateModel(
            name='Portfolio',
            fields=[
                ('profile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='portfolio', serialize=False, to='nc.Profile')),
            ],
        ),
        migrations.CreateModel(
            name='RawPortfolioData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('value', models.FloatField(default=-1.0)),
                ('portfolio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rawdata', to='nc.Portfolio')),
            ],
            options={
                'ordering': ('-created',),
                'abstract': False,
                'get_latest_by': 'created',
            },
        ),
    ]
