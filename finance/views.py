"""Views for the finance app."""

# 1. Standard library imports
#from datetime import date, timedelta
from decimal import Decimal

# 2. Third-party imports (Django)
from django.shortcuts import render, redirect, HttpResponse
from django.views import View
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils.dateparse import parse_date

# 3. First-party imports (your app)
from finance.forms import RegisterForm, TransactionForm, GoalForm
from .models import Trans, Goal
from .admin import TransResource

# Create your views here.
#We will be using Class based view for Register
class WelcomeView(View):
    """ Class to welcome user."""
    def get(self, request):
        """Handle GET request and renders the user to welcome page."""
        return render(request, 'finance/welcome.html')
class RegisterView(View):
    """ Class to register user."""
    def get(self, request):
        """Handle GET request and renders the user to register page ."""
        form = RegisterForm()
        return render(request, 'finance/register.html', {'form': form})
    def post(self, request):
        """Handle POST request and sends the data to form model register page ."""
        form = RegisterForm(request.POST)
        if form.is_valid():
            user  = form.save()
            login(request, user)
            return redirect('dashboard')
        return render(request, 'finance/register.html', {'form': form})
class DashboardView(LoginRequiredMixin, View):
    """ Class to show dashboard user."""
    def get(self, request):
        """Handle GET request and renders the user to dashbard page ."""
        transactions = Trans.objects.filter(user = request.user)
        goals = Goal.objects.filter(user = request.user)
        income_data = (
            Trans.objects
            .filter(user=request.user, transaction_type="income")
            .aggregate(Sum("amount"))
        )
        expense_data = (
            Trans.objects
            .filter(user=request.user, transaction_type="expense")
            .aggregate(Sum("amount"))
        )
        total_income = income_data.get('amount__sum') or 0
        total_expense = expense_data.get('amount__sum') or 0
        net_saving = total_income - total_expense
        remaining_savings = net_saving
        goal_progress = []
        for goal in goals:
            if remaining_savings >= goal.target_amount:
                goal_progress.append({'goal': goal, 'progress': 100})
                remaining_savings -= goal.target_amount
            elif remaining_savings > 0:
                progress = (remaining_savings / goal.target_amount) * 100
                goal_progress.append({'goal': goal, 'progress': progress})
                remaining_savings = 0
            else:
                goal_progress.append({'goal': goal, 'progress': 0})
        context = {
            'transactions': transactions,
            'goals': goals,
            'total_income': total_income,
            'total_expense': total_expense,
            'net_saving': net_saving,
            'goal_progress': goal_progress,
        }
        return render(request, 'finance/dashboard.html', context)
class TransCreateView(LoginRequiredMixin, View):
    """ Class to add transactions of user."""
    def get(self, request):
        """Handle GET request and renders the user to transactions page ."""
        form = TransactionForm()
        return render(request, 'finance/transactions_form.html',{'form': form})
    def post(self, request):
        """Handle POST request and posts the transaction data into model trans ."""
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction  = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect('dashboard')
        return render(request, 'finance/transactions_form.html', {'form': form})
class TransactionListView(LoginRequiredMixin, View):
    """ Class to show user's transaction."""
    def get(self, request):
        """Handle GET request and renders the user to previous transactions page ."""
        transactions = Trans.objects.filter(user=request.user).order_by('-date')
        return render(request, 'finance/transaction_lists.html', {
            'transactions': transactions
        })
class GoalCreateView(LoginRequiredMixin, View):
    """ Class to create user's goal."""
    def get(self, request):
        """Handle GET request and renders the user to goalform page ."""
        form = GoalForm()
        return render(request, 'finance/goal_form.html',{'form': form})
    def post(self, request):
        """Handle POST request and post the data to goal model ."""
        form = GoalForm(request.POST)
        if form.is_valid():
            goal  = form.save(commit=False)
            goal.user = request.user
            goal.save()
            return redirect('dashboard')
        return render(request, 'finance/goal_form.html', {'form': form})
class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    """Class to update user's transaction."""
    model = Trans
    form_class = TransactionForm
    template_name = 'finance/edit_transaction.html'
    success_url = reverse_lazy('transaction_list')

    def get_queryset(self):
        return Trans.objects.filter(user=self.request.user)
class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    """ Class to delete user's transaction."""
    model = Trans
    template_name = 'finance/delete_transaction.html'
    success_url = reverse_lazy('transaction_list')
    def get_queryset(self):
        """Handle GET request ."""
        return Trans.objects.filter(user=self.request.user)
class ExportTransactionsView(LoginRequiredMixin, View):
    # pylint: disable=too-many-locals
    """ Class to export user's past transactions"""
    def get(self, request):
        """Handle GET request and renders the user to export page ."""
        user_transactions = Trans.objects.filter(user=request.user)
        tx_type = request.GET.getlist('type')
        category = request.GET.getlist('category')
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        start_date = parse_date(start_date_str) if start_date_str else None
        end_date = parse_date(end_date_str) if end_date_str else None
        if tx_type in ['income', 'expense']:
            user_transactions = user_transactions.filter(transaction_type__in = tx_type)
        if category:
            user_transactions = user_transactions.filter(category__in = category)
        if start_date:
            user_transactions = user_transactions.filter(date__gte=start_date)
        if end_date:
            user_transactions = user_transactions.filter(date__lte=end_date)
        income_total = (
            user_transactions
            .filter(transaction_type="income")
            .aggregate(Sum("amount"))["amount__sum"]
            or 0
        )
        expense_total = (
            user_transactions
            .filter(transaction_type="expense")
            .aggregate(Sum("amount"))["amount__sum"]
            or 0
        )
        if 'export' in request.GET:
            transactions_resource = TransResource()
            dataset = transactions_resource.export(queryset=user_transactions)
            excel_data = dataset.export('xlsx')
            response = HttpResponse(
                excel_data,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="transactions.xlsx"'
            return response
        # If not exporting, render the form
        context = {
            'transactions': user_transactions,
            'filters': {
                'type': tx_type,
                'category': category,
                'start_date': start_date_str,
                'end_date': end_date_str
            },
            'income_total': income_total, #display total income
            'expense_total': expense_total, #display total expense
            'net_saving': income_total - expense_total,  # Display net saving
        }
        return render(request, 'finance/export.html', context)
class AnalysisView(View):
    # pylint: disable=too-many-locals
    """Class to analyse a user's transactions and show expense/income breakdown."""
    def get(self, request):
        """Handle GET request and renders the user to analysis page ."""
        start_date_str = request.GET.get("start_date")
        end_date_str = request.GET.get("end_date")
        today = now().date()
        start_date = parse_date(str(start_date_str)) if start_date_str else None
        end_date = parse_date(str(end_date_str)) if end_date_str else None
        show_charts = bool(start_date and end_date)
        
        # Base querysets
            
        expenses = Trans.objects.filter(user=request.user, transaction_type="expense")
        income = Trans.objects.filter(user=request.user, transaction_type="income")
        
        if start_date:
            expenses = expenses.filter(date__gte=start_date)
            income = income.filter(date__gte=start_date)
        
        if end_date:
            expenses = expenses.filter(date__lte=end_date)
            income = income.filter(date__lte=end_date)
        # Aggregate by category
        category_expenses = expenses.values("category").annotate(total=Sum("amount"))
        category_income = income.values("category").annotate(total=Sum("amount"))

        expense_labels = [entry["category"].capitalize() for entry in category_expenses]
        expense_data = [float(entry["total"]) for entry in category_expenses]
        income_labels = [entry["category"].capitalize() for entry in category_income]
        income_data = [float(entry["total"]) for entry in category_income]
        # Build summary
        total_expense = sum(Decimal(entry["total"]) for entry in category_expenses)
        if total_expense > 0:
            summary_parts = [
                f"{(entry['total'] / total_expense * 100):.2f}% was spent on {entry['category']}"
                for entry in category_expenses
            ]
            summarise = "\n".join(summary_parts)
        else:
            summarise = (
                f"No expenses found from {start_date.strftime('%d %B %Y')} "
                f"to {end_date.strftime('%d %B %Y')}."
            )
        context = {
            "expense_labels": expense_labels,
            "expense_data": expense_data,
            "income_labels": income_labels,
            "income_data": income_data,
            "summarise": summarise,
            "show_charts": show_charts,
        }
        return render(request, "finance/analysis.html", context)
        