# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-11 12:17
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("thiamsu", "0003_auto_20171029_1439")]

    operations = [
        migrations.RenameField(
            model_name="song", old_name="singer", new_name="performer"
        )
    ]
