"""Database models for the finance app.

Defines transaction and goal models used to track user finances.
"""

from django.db import models
from django.contrib.auth.models import User


class Trans(models.Model):
    """Model representing a financial transaction taht is income or expense."""

    TRANSACTION_TYPES = [
        ("income", "Income"),
        ("expense", "Expense"),
    ]

    CATEGORY_CHOICES = [
        ("salary", "Salary"),
        ("business", "Business"),
        ("food", "Food"),
        ("entertainment", "Entertainment"),
        ("utilities", "Utilities"),
        ("transportation", "Transportation"),
        ("health", "Health"),
        ("others", "Others"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    date = models.DateField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    def __str__(self):
        return str(self.title)


class Goal(models.Model):
    """Model representing a financial goal set by a user."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deadline = models.DateField()

    def __str__(self):
        return str(self.name)