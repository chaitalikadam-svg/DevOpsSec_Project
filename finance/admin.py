"""Admin configuration for the finance app."""

from django.contrib import admin
from import_export import resources
from import_export.admin import ExportMixin
from .models import Trans, Goal


class TransResource(resources.ModelResource):
    """Resource class for exporting transaction data."""

    class Meta:
        model = Trans
        fields = (
            "user__username",
            "title",
            "amount",
            "transaction_type",
            "date",
            "category",
        )


class TransAdmin(ExportMixin, admin.ModelAdmin):
    """Admin configuration for transactions with export functionality."""

    resource_class = TransResource
    list_display = ("title", "user", "amount", "transaction_type", "date", "category")
    list_filter = ("transaction_type", "category", "date")
    search_fields = ("title", "user__username")


# Register models with the admin site
admin.site.register(Trans, TransAdmin)
admin.site.register(Goal)