"""
URL configuration for expensetracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from . import views

from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('authentication/', include('authentication.urls')),
    path('preferences/', include('userpreferences.urls')),
    path('income/', include('userincome.urls')),
    path('forecast/', include('expense_forecast.urls')),
    path('api/', include('api.urls')),
    path('goals/', include('goals.urls')),
    path('account/', include('userprofile.urls')),
    path('expenses/', include('expenses.urls')),
    path('report_generation/', include('report_generation.urls')),
    path('data_upload/', include('data_upload.urls')),
]
