# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-19 13:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
        ('invitations', '0003_auto_20151126_1523'),
    ]

    operations = [
        migrations.AddField(
            model_name='invitation',
            name='group',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invitation', to='auth.Group'),
        ),
    ]
