"""App configuration for the finance app."""

from django.apps import AppConfig


class FinanceConfig(AppConfig):
    """Configuration class for the finance app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "finance"
    