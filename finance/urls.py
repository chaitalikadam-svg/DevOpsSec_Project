from django.urls import path
from finance.views import RegisterView, DashboardView, TransCreateView, TransactionListView, GoalCreateView, ExportTransactionsView, TransactionUpdateView, TransactionDeleteView, AnalysisView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('', DashboardView.as_view(), name='dashboard'),
    path('transaction/add/', TransCreateView.as_view(), name='add_transaction'),
    path('transactions/', TransactionListView.as_view(), name='transaction_list'),  
    path('goal/add/', GoalCreateView.as_view(), name='goal_add'),  
    path('generate-report/', ExportTransactionsView.as_view(), name='export_transactions'),  
    path('transaction/<int:pk>/edit/', TransactionUpdateView.as_view(), name='transaction_edit'),  
    path('transaction/<int:pk>/delete/', TransactionDeleteView.as_view(), name='transaction_delete'),  
    path('analysis/', AnalysisView.as_view(), name='analysis'),
]