from django.shortcuts import render, redirect,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .models import Category, Expense, ExpenseLimit
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from userpreferences.models import UserPreference
import datetime
import requests
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Sum

try:
    import pandas as pd
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.ensemble import RandomForestClassifier
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    import nltk

    data = pd.read_csv('dataset.csv')

    # Preprocessing
    stop_words = set(stopwords.words('english'))

    def preprocess_text(text):
        tokens = word_tokenize(text.lower())
        tokens = [t for t in tokens if t.isalnum() and t not in stop_words]
        return ' '.join(tokens)

    data['clean_description'] = data['description'].apply(preprocess_text)

    # Feature extraction
    tfidf_vectorizer = TfidfVectorizer()
    X = tfidf_vectorizer.fit_transform(data['clean_description'])

    # Train a RandomForestClassifier
    model = RandomForestClassifier()
    model.fit(X, data['category'])
except ImportError:
    # Define dummy variables and functions if pandas or sklearn is not available
    data = None
    tfidf_vectorizer = None
    model = None

    def preprocess_text(text):
        return text
@login_required(login_url='/authentication/login')
def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            date__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            description__icontains=search_str, owner=request.user) | Expense.objects.filter(
            category__icontains=search_str, owner=request.user)
        data = expenses.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/authentication/login')
def expenses_list(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)

    sort_order = request.GET.get('sort')

    if sort_order == 'amount_asc':
        expenses = expenses.order_by('amount')
    elif sort_order == 'amount_desc':
        expenses = expenses.order_by('-amount')
    elif sort_order == 'date_asc':
        expenses = expenses.order_by('date')
    elif sort_order == 'date_desc':
        expenses = expenses.order_by('-date')

    paginator = Paginator(expenses, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    try:
        currency = UserPreference.objects.get(user=request.user).currency
    except:
        currency=None

    total = page_obj.paginator.num_pages
    context = {
        'expenses': expenses,
        'page_obj': page_obj,
        'currency': currency,
        'total': total,
        'sort_order': sort_order,

    }
    return render(request, 'expenses/index.html', context)

daily_expense_amounts = {}

from django.views import View
from django.utils.decorators import method_decorator

@method_decorator(login_required(login_url='/authentication/login'), name='dispatch')
class AddExpenseView(View):
    def get(self, request):
        categories = Category.objects.all()
        context = {
            'categories': categories,
            'values': {}
        }
        return render(request, 'expenses/add_expense.html', context)

    def post(self, request):
        categories = Category.objects.all()
        context = {
            'categories': categories,
            'values': request.POST
        }
        amount = request.POST.get('amount')
        date_str = request.POST.get('expense_date')

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/add_expense.html', context)
        description = request.POST.get('description')
        predicted_category = request.POST.get('category')

        if not description:
            messages.error(request, 'Description is required')
            return render(request, 'expenses/add_expense.html', context)

        initial_predicted_category = request.POST.get('initial_predicted_category')
        if predicted_category != initial_predicted_category:
            new_data = {
                'description': description,
                'category': predicted_category,
            }
            update_url = 'http://127.0.0.1:8000/api/update-dataset/'
            response = requests.post(update_url, json={'new_data': new_data})

        try:
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            today = datetime.date.today()

            if date > today:
                messages.error(request, 'Date cannot be in the future')
                return render(request, 'expenses/add_expense.html', context)

            user = request.user
            expense_limits = ExpenseLimit.objects.filter(owner=user)
            if expense_limits.exists():
                daily_expense_limit = expense_limits.first().daily_expense_limit
            else:
                daily_expense_limit = 5000

            total_expenses_today = get_expense_of_day(user) + float(amount)
            if total_expenses_today > daily_expense_limit:
                subject = 'Daily Expense Limit Exceeded'
                message = f'Hello {user.username},\n\nYour expenses for today have exceeded your daily expense limit. Please review your expenses.'
                from_email = settings.EMAIL_HOST_USER
                to_email = [user.email]
                send_mail(subject, message, from_email, to_email, fail_silently=False)
                messages.warning(request, 'Your expenses for today exceed your daily expense limit')

            Expense.objects.create(owner=user, amount=amount, date=date,
                                   category=predicted_category, description=description)
            messages.success(request, 'Expense saved successfully')
            return redirect('expenses')
        except ValueError:
            messages.error(request, 'Invalid date format')
            return render(request, 'expenses/add_expense.html', context)


@login_required(login_url='/authentication/login')
def expense_edit(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    context = {
        'expense': expense,
        'values': expense,
        'categories': categories
    }
    if request.method == 'GET':
        return render(request, 'expenses/edit-expense.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']
        date_str = request.POST.get('expense_date')

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/edit-expense.html', context)
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'expenses/edit-expense.html', context)

        try:
            # Convert the date string to a datetime object and validate the date
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            today = datetime.date.today()

            if date > today:
                messages.error(request, 'Date cannot be in the future')
                return render(request, 'expenses/add_expense.html', context)

            expense.owner = request.user
            expense.amount = amount
            expense. date = date
            expense.category = category
            expense.description = description

            expense.save()
            messages.success(request, 'Expense saved successfully')

            return redirect('expenses')
        except ValueError:
            messages.error(request, 'Invalid date format')
            return render(request, 'expenses/edit_income.html', context)

        # expense.owner = request.user
        # expense.amount = amount
        # expense. date = date
        # expense.category = category
        # expense.description = description

        # expense.save()

        # messages.success(request, 'Expense updated  successfully')

        # return redirect('expenses')

@login_required(login_url='/authentication/login')
def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Expense removed')
    return redirect('expenses')

@login_required(login_url='/authentication/login')
def expense_category_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date-datetime.timedelta(days=30*6)
    expenses = Expense.objects.filter(owner=request.user,
                                      date__gte=six_months_ago, date__lte=todays_date)
    finalrep = {}

    def get_category(expense):
        return expense.category
    category_list = list(set(map(get_category, expenses)))

    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category = expenses.filter(category=category)

        for item in filtered_by_category:
            amount += item.amount
        return amount

    for x in expenses:
        for y in category_list:
            finalrep[y] = get_expense_category_amount(y)

    return JsonResponse({'expense_category_data': finalrep}, safe=False)

@login_required(login_url='/authentication/login')
def expense_summary(request):
    import numpy as np
    try:
        import pandas as pd
        from statsmodels.tsa.arima.model import ARIMA
    except ImportError:
        pd = None
        ARIMA = None

    user = request.user  # Get the logged-in user

    today = datetime.date.today()
    one_week_ago = today - datetime.timedelta(days=7)
    first_day_of_month = today.replace(day=1)
    first_day_of_year = today.replace(month=1, day=1)

    # Query the database to get daily, weekly, monthly, and yearly expenses for the logged-in user
    daily_expense = Expense.objects.filter(owner=user, date=today).aggregate(Sum('amount'))['amount__sum'] or 0
    weekly_expense = Expense.objects.filter(owner=user, date__range=[one_week_ago, today]).aggregate(Sum('amount'))['amount__sum'] or 0
    monthly_expense = Expense.objects.filter(owner=user, date__month=today.month).aggregate(Sum('amount'))['amount__sum'] or 0
    yearly_expense = Expense.objects.filter(owner=user, date__year=today.year).aggregate(Sum('amount'))['amount__sum'] or 0

    # Fetch the latest 30 expenses for the current user for forecasting
    expenses = Expense.objects.filter(owner=user).order_by('-date')[:30]

    if pd is None or ARIMA is None:
        forecast_data_list = []
        total_forecasted_expenses = 0
        category_forecasts = {}
    else:
        # Create a DataFrame from the expenses
        data = pd.DataFrame({'Date': [expense.date for expense in expenses], 'Expenses': [expense.amount for expense in expenses], 'Category': [expense.category for expense in expenses]})
        data.set_index('Date', inplace=True)

        # Fit ARIMA model
        model = ARIMA(data['Expenses'], order=(5, 1, 0))
        try:
            model_fit = model.fit(disp=0)
        except Exception as e:
            model_fit = None

        # Forecast next 30 days of expenses starting from the next day
        forecast_steps = 30
        next_day = today + pd.DateOffset(days=1)
        forecast_index = pd.date_range(start=next_day, periods=forecast_steps, freq='D')

        if model_fit:
            # Predict the future expenses
            forecast = model_fit.forecast(steps=forecast_steps)

            # Create a DataFrame for the forecasted expenses
            forecast_data = pd.DataFrame({'Date': forecast_index, 'Forecasted_Expenses': forecast})

            # Convert the forecast data to a list of dictionaries
            forecast_data_list = forecast_data.reset_index().to_dict(orient='records')

            # Calculate total forecasted expenses
            total_forecasted_expenses = np.sum(forecast)
        else:
            forecast_data_list = []
            total_forecasted_expenses = 0

        # Calculate total forecasted expenses per category
        category_forecasts = data.groupby('Category')['Expenses'].sum().to_dict()

    context = {
        'daily_expense': daily_expense,
        'weekly_expense': weekly_expense,
        'monthly_expense': monthly_expense,
        'yearly_expense': yearly_expense,
        'forecast_data': forecast_data_list,
        'total_forecasted_expenses': total_forecasted_expenses,
        'category_forecasts': category_forecasts,
    }
    # Replace Indian Rupee symbol with "Rs." in context values if any string
    for key, value in context.items():
        if isinstance(value, str):
            currency_symbols = ['₹', '$', '€', '£', '¥']
            for symbol in currency_symbols:
                value = value.replace(symbol, '')
            context[key] = value
    return render(request, 'expenses/summary.html', context)

@login_required(login_url='/authentication/login')
def stats_view(request):
    return render(request, 'expenses/stats.html')

@login_required(login_url='/authentication/login')
def predict_category(description):
    predict_category_url = 'http://localhost:8000/api/predict-category/'  # Use the correct URL path
    data = {'description': description}
    response = requests.post(predict_category_url, data=data)

    if response.status_code == 200:
        # Get the predicted category from the response
        predicted_category = response.json().get('predicted_category')
        return predicted_category
    else:
        # Handle the case where the prediction request failed
        return None
    

def set_expense_limit(request):
    if request.method == "POST":
        daily_expense_limit = request.POST.get('daily_expense_limit')
        
        existing_limit = ExpenseLimit.objects.filter(owner=request.user).first()
        
        if existing_limit:
            existing_limit.daily_expense_limit = daily_expense_limit
            existing_limit.save()
        else:
            ExpenseLimit.objects.create(owner=request.user, daily_expense_limit=daily_expense_limit)
        
        messages.success(request, "Daily Expense Limit Updated Successfully!")
        return HttpResponseRedirect('/preferences/')
    else:
        return HttpResponseRedirect('/preferences/')
    
from datetime import date

def get_expense_of_day(user):
    current_date=date.today()
    expenses=Expense.objects.filter(owner=user,date=current_date)
    total_expenses=sum(expense.amount for expense in expenses)
    return total_expenses
    