# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-19 13:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('invitations', '0004_invitation_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitation',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invitation', to='auth.Group'),
        ),
    ]
