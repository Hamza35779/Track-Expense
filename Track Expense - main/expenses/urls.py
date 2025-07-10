from django.urls import path
from . import views

from django.views.decorators.csrf import csrf_exempt

from django.urls import path
from . import views

from django.urls import path
from . import views

from django.urls import path
from . import views

from django.urls import path
from . import views

urlpatterns = [
    path('', views.expenses_list, name='expenses'),
    path('add/', views.AddExpenseView.as_view(), name='add-expenses'),
    path('edit/<int:id>/', views.expense_edit, name='expense-edit'),
    path('delete/<int:id>/', views.delete_expense, name='delete-expenses'),
    path('summary/', views.expense_summary, name='expense-summary'),
]
