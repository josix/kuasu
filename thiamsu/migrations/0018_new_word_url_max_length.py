# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-07-03 12:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("thiamsu", "0017_translation_lang_hanlo")]

    operations = [
        migrations.AlterField(
            model_name="newword",
            name="reference_url",
            field=models.CharField(
                max_length=1000, verbose_name="new_word_reference_url"
            ),
        )
    ]
