# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-24 18:27
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("thiamsu", "0010_auto_20171124_1825")]

    operations = [
        migrations.AlterUniqueTogether(
            name="approvedtranslation", unique_together=set([])
        ),
        migrations.RemoveField(model_name="approvedtranslation", name="reviewer"),
        migrations.RemoveField(model_name="approvedtranslation", name="song"),
        migrations.RemoveField(model_name="approvedtranslation", name="translation"),
        migrations.DeleteModel(name="ApprovedTranslation"),
    ]
