from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name="preferences"),
    path('set-daily-expense-limit/', views.set_daily_expense_limit, name='set-daily-expense-limit'),
]
