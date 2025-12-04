from django.shortcuts import render, redirect, HttpResponse
from django.views import View
from finance.forms import RegisterForm
from finance.forms import TransactionForm
from finance.forms import GoalForm
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Trans, Goal
from django.db.models import Sum
from .admin import TransResource
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy 
from django.utils.dateparse import parse_date # to filter out the date for export
from datetime import date, timedelta
from decimal import Decimal
from django.http import HttpResponse

# Create your views here.
#We will be using Class based view for Register
class WelcomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'finance/welcome.html')

        
class RegisterView(View):
    def get(self, request, *args, **kwargs):
        form = RegisterForm()
        return render(request, 'finance/register.html', {'form': form})
    
    def post(self, request, *args, **kwargs):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user  = form.save()
            login(request, user)
            return redirect('dashboard')
        return render(request, 'finance/register.html', {'form': form})
    
class DashboardView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
            
        transactions = Trans.objects.filter(user = request.user)
        goals = Goal.objects.filter(user = request.user)

        income_data = Trans.objects.filter(user=request.user, transaction_type='income').aggregate(Sum('amount'))
        expense_data = Trans.objects.filter(user=request.user, transaction_type='expense').aggregate(Sum('amount'))

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
    def get(self, request, *args, **kwargs):
        form = TransactionForm()
        return render(request, 'finance/transactions_form.html',{'form': form})
    
    def post(self, request, *args, **kwargs):
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction  = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect('dashboard')
        return render(request, 'finance/transactions_form.html', {'form': form})
    
class TransactionListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        transactions = Trans.objects.filter(user=request.user).order_by('-date')
        return render(request, 'finance/transaction_lists.html', {
            'transactions': transactions
        })
    
class GoalCreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = GoalForm()
        return render(request, 'finance/goal_form.html',{'form': form})
    
    def post(self, request, *args, **kwargs):
        form = GoalForm(request.POST)
        if form.is_valid():
            goal  = form.save(commit=False)
            goal.user = request.user
            goal.save()
            return redirect('dashboard')
        return render(request, 'finance/goal_form.html', {'form': form})
    
class ExportTransactionsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
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
            
        income_total = user_transactions.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
        expense_total = user_transactions.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0



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



class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Trans
    fields = ['title', 'amount', 'transaction_type', 'category', 'date']  # adjust as needed
    template_name = 'finance/edit_transaction.html'
    success_url = reverse_lazy('transaction_list')

    def get_queryset(self):
        return Trans.objects.filter(user=self.request.user)

class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = Trans
    template_name = 'finance/delete_transaction.html'
    success_url = reverse_lazy('transaction_list')

    def get_queryset(self):
        return Trans.objects.filter(user=self.request.user)
    
class AnalysisView(View):
    def get(self, request, *args, **kwargs):
        expense_labels = []
        expense_data = []
        income_labels = []
        income_data = []
        summarise = ""
        
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        
        
        # Ensure values are strings before parsing
        start_date = parse_date(str(start_date_str)) if start_date_str else None
        end_date = parse_date(str(end_date_str)) if end_date_str else None
        
        show_charts = bool(start_date and end_date)
        
        expenses = Trans.objects.filter(user=request.user, transaction_type='expense')
        income = Trans.objects.filter(user=request.user, transaction_type='income')


        if start_date:
            expenses = expenses.filter(date__gte=start_date)
        if end_date:
            expenses = expenses.filter(date__lte=end_date)
        

        # Aggregate by category
        category_expenses = expenses.values('category').annotate(total=Sum('amount'))
        category_income = income.values('category').annotate(total=Sum('amount'))

        expense_labels = [entry['category'].capitalize() for entry in category_expenses]
        expense_data = [float(entry['total']) for entry in category_expenses]

        income_labels = [entry['category'].capitalize() for entry in category_income]
        income_data = [float(entry['total']) for entry in category_income]
        
        total_expense = sum(Decimal(entry['total']) for entry in category_expenses)

        if total_expense > 0:
            summary_parts = [
                f"{(entry['total'] / total_expense * 100):.2f}% was spent on {entry['category']}"
                for entry in category_expenses
            ]
            summarise = "\n".join(summary_parts)
        else:
            summarise = f"No expenses found from {start_date.strftime('%d %B %Y')} to {end_date.strftime('%d %B %Y')}."

        context = {
            'expense_labels': expense_labels,
            'expense_data': expense_data,
            'income_labels': income_labels,
            'income_data': income_data,
            'summarise': summarise,
            'show_charts': show_charts
        }
        return render(request, 'finance/analysis.html', context)


