# Generated by Django 4.1.2 on 2022-10-26 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accident", "0002_post_isaccident"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="predicted",
            field=models.BooleanField(default=False),
        ),
    ]
