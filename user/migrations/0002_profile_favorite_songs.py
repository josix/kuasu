# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-19 14:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("thiamsu", "0007_auto_20171112_2017"), ("user", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="favorite_songs",
            field=models.ManyToManyField(
                related_name="_profile_favorite_songs_+", to="thiamsu.Song"
            ),
        )
    ]
