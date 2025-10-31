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


# Create your views here.
#We will be using Class based view for Register

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
        transactions = Trans.objects.filter(user=request.user)
        return render(request, 'finance/transaction_lists.html' ,
                                            {'transactions': transactions})
    
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
        transactions_resource = TransResource()
        dataset = transactions_resource.export(queryset = user_transactions)

        excel_data = dataset.xlsx

        response = HttpResponse(excel_data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

        response['Content-Disposition'] = 'attachment; filename="transactions.xlsx"'
        return response

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
        expenses = Trans.objects.filter(user=request.user, transaction_type='expense')
        income = Trans.objects.filter(user=request.user, transaction_type='income')

        # Aggregate by category
        category_expenses = expenses.values('category').annotate(total=Sum('amount'))
        category_income = income.values('category').annotate(total=Sum('amount'))

        expense_labels = [entry['category'].capitalize() for entry in category_expenses]
        expense_data = [float(entry['total']) for entry in category_expenses]

        income_labels = [entry['category'].capitalize() for entry in category_income]
        income_data = [float(entry['total']) for entry in category_income]

        context = {
            'expense_labels': expense_labels,
            'expense_data': expense_data,
            'income_labels': income_labels,
            'income_data': income_data,
        }
        return render(request, 'finance/analysis.html', context)


