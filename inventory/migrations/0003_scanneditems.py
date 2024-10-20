# Generated by Django 5.0.3 on 2024-05-07 07:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0002_product"),
    ]

    operations = [
        migrations.CreateModel(
            name="scannedItems",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("units", models.IntegerField(default=0)),
                ("fragile", models.BooleanField(default=False)),
                ("weight", models.FloatField(default=0)),
                ("unit", models.CharField(max_length=50)),
                ("item_class", models.CharField(max_length=50)),
            ],
        ),
    ]