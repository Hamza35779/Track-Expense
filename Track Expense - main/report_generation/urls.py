from django.urls import path
from . import views

urlpatterns = [
    path('income-expense-report/', views.income_expense_report, name='income-expense-report'),
    path('export/pdf/', views.export_pdf, name='export-pdf'),
    path('export/csv/', views.export_csv, name='export-csv'),
    path('export/xlsx/', views.export_xlsx, name='export-xlsx'),
]
