# Generated by Django 5.2.3 on 2025-06-24 06:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="candidatescore",
            options={"ordering": ["-date_recorded"]},
        ),
        migrations.RenameField(
            model_name="candidatescore",
            old_name="date_taken",
            new_name="date_recorded",
        ),
    ]
