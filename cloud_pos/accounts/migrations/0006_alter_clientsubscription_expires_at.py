# Generated by Django 5.1.2 on 2025-06-09 13:06

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0005_alter_user_options_remove_clientsubscription_user_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="clientsubscription",
            name="expires_at",
            field=models.DateTimeField(
                default=1,
                verbose_name=datetime.datetime(
                    2026, 6, 9, 13, 6, 36, 860879, tzinfo=datetime.timezone.utc
                ),
            ),
        ),
    ]
