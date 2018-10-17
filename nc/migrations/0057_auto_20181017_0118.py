# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-17 01:18
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('nc', '0056_auto_20181014_1424'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity_id', models.CharField(blank=True, default=None, max_length=36, null=True)),
                ('tx_hash', models.CharField(blank=True, default=None, max_length=64, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('verb', models.IntegerField(choices=[(0, 'post'), (1, 'send'), (2, 'issue'), (3, 'trust'), (4, 'offer'), (5, 'follow')], default=0)),
                ('liked_by', models.ManyToManyField(blank=True, related_name='activities_liked', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity_id', models.CharField(blank=True, default=None, max_length=36, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('liked_by', models.ManyToManyField(blank=True, related_name='comments_liked', to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='nc.Activity')),
            ],
        ),
        migrations.CreateModel(
            name='Reward',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tx_hash', models.CharField(max_length=64)),
                ('xlm_value', models.FloatField(default=0.0)),
                ('activity', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rewards', to='nc.Activity')),
                ('comment', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rewards', to='nc.Comment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rewards_given_out', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='rewarded_by',
            field=models.ManyToManyField(blank=True, related_name='comments_rewarded', through='nc.Reward', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='activity',
            name='rewarded_by',
            field=models.ManyToManyField(blank=True, related_name='activities_rewarded', through='nc.Reward', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='activity',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to=settings.AUTH_USER_MODEL),
        ),
    ]