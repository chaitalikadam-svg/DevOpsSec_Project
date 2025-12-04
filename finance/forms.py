from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Trans, Goal
from django.utils.timezone import now


class RegisterForm(UserCreationForm): #Show users data in admin page
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2'] 

class TransactionForm(forms.ModelForm): #Show trasactions of all users in admin page
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
        else :
            self.fields['category'].choices = [
                ('food', 'Food'),
                ('entertainment', 'Entertainment'),
                ('utilities', 'Utilities'),
                ('transportation', 'Transportation'),
                ('health', 'Health'),
                ('others', 'Others')
            ]
                
    def clean_date(self): #Validation so that while adding transaction date should not be future date
        selected_date = self.cleaned_data.get('date')
        if selected_date and selected_date > now().date():
            raise forms.ValidationError("Date cannot be in the future.")
        return selected_date

class GoalForm(forms.ModelForm): #show goals to django admin
    class Meta:
        model = Goal
        fields = ['name', 'target_amount', 'deadline'] 