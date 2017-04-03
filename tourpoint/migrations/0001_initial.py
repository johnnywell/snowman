# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-02 21:37
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TourPoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name for the tour point', max_length=100)),
                ('longitude', models.FloatField(help_text='longitude for the current position')),
                ('latitude', models.FloatField(help_text='latitude for the current position')),
                ('private', models.BooleanField(default=False, help_text='To make this a private tour point')),
                ('category', models.CharField(choices=[('restaurant', 'restaurant'), ('museum', 'museum'), ('park', 'park')], help_text='Which kind of tour point it is?', max_length=10)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(help_text='Who created this tour point.', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]