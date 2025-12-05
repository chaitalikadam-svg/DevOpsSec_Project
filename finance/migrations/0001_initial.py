# pylint: disable=invalid-name
"""Initial migration for the finance app."""

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """Initial database schema migration for the finance app."""

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Trans",
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
                ("title", models.CharField(max_length=100)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "transaction_type",
                    models.CharField(
                        choices=[("income", "Income"), ("expense", "Expense")],
                        max_length=7,
                    ),
                ),
                ("date", models.DateField()),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("salary", "Salary"),
                            ("business", "Business"),
                            ("food", "Food"),
                            ("entertainment", "Entertainment"),
                            ("utilities", "Utilities"),
                            ("transportation", "Transportation"),
                            ("health", "Health"),
                            ("others", "Others"),
                        ],
                        max_length=50,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
    