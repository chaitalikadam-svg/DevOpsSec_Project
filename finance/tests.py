""" TestCases for the finance app."""
from datetime import date
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from finance.models import Trans

User = get_user_model()

class TestAnalysisView(TestCase):
    """Below are the different type of test cases"""
    def setUp(self):
        """Create test user adding income and expense"""
        self.user = User.objects.create_user(
            username="tester", email="test@example.com", password="pass1234"
        )
        self.client.login(username="tester", password="pass1234")

        # Initial transactions
        Trans.objects.create(
            user=self.user,
            transaction_type="income",
            category="Salary",
            amount=100,
            date=date(2024, 1, 15)
        )
        Trans.objects.create(
            user=self.user,
            transaction_type="expense",
            category="Food",
            amount=50,
            date=date(2024, 1, 20)
        )

    def test_analysis_with_date_filters(self):
        """Filters transactions within that date range"""
        response = self.client.get(
            reverse("analysis"),
            {"start_date": "2024-01-01", "end_date": "2024-01-31"}
        )
        self.assertEqual(response.status_code, 200)
        ctx = response.context
        self.assertEqual(ctx["income_data"], [100.0])
        self.assertEqual(ctx["expense_data"], [50.0])
        self.assertTrue(ctx["show_charts"])

    def test_analysis_expense_zero_summary(self):
        """No expense"""
        Trans.objects.filter(transaction_type="expense").delete()
        response = self.client.get(
            reverse("analysis"),
            {"start_date": "2024-01-01", "end_date": "2024-01-31"}
        )
        ctx = response.context
        self.assertIn("No expenses found", ctx["summarise"])

    def test_analysis_missing_dates(self):
        """No date filter"""
        response = self.client.get(reverse("analysis"))
        ctx = response.context
        self.assertFalse(ctx["show_charts"])
        self.assertTrue("income_data" in ctx and "expense_data" in ctx)

    def test_analysis_invalid_dates(self):
        """Invalid date"""
        response = self.client.get(
            reverse("analysis"),
            {"start_date": "invalid", "end_date": "2024-01-31"}
        )
        self.assertEqual(response.status_code, 200)

    def test_multiple_categories(self):
        """multiple category"""
        Trans.objects.create(
            user=self.user,
            transaction_type="income",
            category="Bonus",
            amount=200,
            date=date(2024, 1, 10),
        )
        Trans.objects.create(
            user=self.user,
            transaction_type="expense",
            category="Rent",
            amount=500,
            date=date(2024, 1, 12)
        )
        response = self.client.get(
            reverse("analysis"),
            {"start_date": "2024-01-01", "end_date": "2024-01-31"}
        )
        ctx = response.context
        self.assertEqual(set(ctx["income_labels"]), {"Salary", "Bonus"})
        self.assertEqual(set(ctx["expense_labels"]), {"Food", "Rent"})

    def test_transactions_outside_date_range(self):
        """Exclude trasactions outside date range"""
        Trans.objects.create(
            user=self.user,
            transaction_type="income",
            category="Gift",
            amount=300,
            date=date(2023, 12, 31)
        )
        response = self.client.get(
            reverse("analysis"),
            {"start_date": "2024-01-01", "end_date": "2024-01-31"}
        )
        ctx = response.context
        self.assertEqual(ctx["income_data"], [100.0])

    def test_different_user_transactions(self):
        """Other users trasactions should be excluded"""
        other_user = User.objects.create_user(
            username="other", email="other@example.com", password="pass1234"
        )
        Trans.objects.create(
            user=other_user,
            transaction_type="income",
            category="Salary",
            amount=999,
            date=date(2024, 1, 15)
        )
        response = self.client.get(reverse("analysis"))
        ctx = response.context
        self.assertEqual(ctx["income_data"], [100.0])
