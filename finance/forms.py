from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Trans, Goal

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Trans
        fields = ['title', 'amount', 'transaction_type', 'date', 'category']    
    def __init__(self, *args, **kwargs):
        transaction_type = kwargs.pop('transaction_type', None)
        super().__init__(*args, **kwargs)

        if transaction_type == 'income':
            self.fields['category'].choices = [
                ('salary', 'Salary'),
                ('business', 'Business'),
            ]
        elif transaction_type == 'expense':
            self.fields['category'].choices = [
                ('food', 'Food'),
                ('entertainment', 'Entertainment'),
                ('utilities', 'Utilities'),
                ('transportation', 'Transportation'),
                ('health', 'Health'),
                ('others', 'Others'),
            ]

class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['name', 'target_amount', 'deadline'] 