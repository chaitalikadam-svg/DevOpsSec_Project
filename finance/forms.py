"""Forms configuration for the finance app."""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.timezone import now
from .models import Trans, Goal


class RegisterForm(UserCreationForm):
    """Form for registering new users."""

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class TransactionForm(forms.ModelForm):
    """Form for creating and editing transactions."""

    class Meta:
        model = Trans
        fields = ["title", "amount", "transaction_type", "date", "category"]

    def __init__(self, *args, **kwargs):
        """Initialize transaction form with category choices based on type."""
        transaction_type = kwargs.pop("transaction_type", None)
        super().__init__(*args, **kwargs)

        if transaction_type == "income":
            self.fields["category"].choices = [
                ("salary", "Salary"),
                ("business", "Business"),
            ]
        else:
            self.fields["category"].choices = [
                ("food", "Food"),
                ("entertainment", "Entertainment"),
                ("utilities", "Utilities"),
                ("transportation", "Transportation"),
                ("health", "Health"),
                ("others", "Others"),
            ]

    def clean_date(self):
        """Ensure transaction date is not set in the future."""
        selected_date = self.cleaned_data.get("date")
        if selected_date and selected_date > now().date():
            raise forms.ValidationError("Date cannot be in the future.")
        return selected_date


class GoalForm(forms.ModelForm):
    """Form for creating and editing financial goals."""

    class Meta:
        model = Goal
        fields = ["name", "target_amount", "deadline"]