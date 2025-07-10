from django.shortcuts import render
import numpy as np
try:
    import pandas as pd
    from statsmodels.tsa.arima.model import ARIMA
    import matplotlib.pyplot as plt
except ImportError:
    pd = None
    ARIMA = None
    plt = None

from django.utils.timezone import now
from expenses.models import Expense
from userincome.models import UserIncome
from django.http import HttpResponse
from django.contrib import messages


# Fetch the data from the Expense model and create the forecast
def index(request):
    # Fetch the latest 30 expenses for the current user
    if request.user.is_authenticated:
        expenses = Expense.objects.filter(owner=request.user).order_by('-date')[:30]
        incomes = UserIncome.objects.filter(owner=request.user).order_by('-date')[:30]
    else:
        expenses = []
        incomes = []

    # Check if there are enough expenses for forecasting
    if len(expenses) < 3:
        messages.error(request, "Not enough expenses to make a forecast. Please add more expenses.")
        return render(request, 'expense_forecast/index.html')

    if pd is None or ARIMA is None or plt is None:
        messages.error(request, "Forecasting feature is not available because required packages are not installed.")
        return render(request, 'expense_forecast/index.html')

    # Create a DataFrame from the expenses with scaled down amounts for better visualization
    data = pd.DataFrame({'Date': [expense.date for expense in expenses], 'Expenses': [expense.amount / 100 for expense in expenses], 'Category': [expense.category for expense in expenses]})
    data.set_index('Date', inplace=True)

    # Log expense amounts for debugging
    print("Expense amounts for forecasting:", data['Expenses'].tolist())

    # Sort data by date and set frequency to daily
    data = data.sort_index()
    data.index = pd.DatetimeIndex(data.index)
    data = data.asfreq('D')

    # Apply rolling mean smoothing with window size 3
    data['Expenses_Smoothed'] = data['Expenses'].rolling(window=3, min_periods=1).mean()

    # Create a DataFrame from the incomes
    income_data = pd.DataFrame({'Date': [income.date for income in incomes], 'Income': [income.amount for income in incomes], 'Source': [income.source for income in incomes]})
    income_data.set_index('Date', inplace=True)

    # Fit ARIMA model on smoothed data with simpler parameters
    model = ARIMA(data['Expenses_Smoothed'], order=(1, 1, 1))
    model_fit = model.fit()

    # Forecast next 30 days of expenses starting from the next day
    forecast_steps = 30
    current_date = now().date()
    next_day = current_date + pd.DateOffset(days=1)
    forecast_index = pd.date_range(start=next_day, periods=forecast_steps, freq='D')

    # Predict the future expenses
    forecast = model_fit.forecast(steps=forecast_steps)

    # Create a DataFrame for the forecasted expenses
    forecast_data = pd.DataFrame({'Date': forecast_index, 'Forecasted_Expenses': forecast})
    
    # Convert the forecast data to a list of dictionaries
    forecast_data_list = forecast_data.reset_index().to_dict(orient='records')

    # Calculate total forecasted expenses
    total_forecasted_expenses = np.sum(forecast)

    # Calculate total forecasted expenses per category
    category_forecasts = data.groupby('Category')['Expenses'].sum().to_dict()

    # Calculate total income and expenses summaries
    total_income = income_data['Income'].sum() if not income_data.empty else 0
    total_expenses = data['Expenses'].sum() if not data.empty else 0

    # Create a plot but save it without displaying it
    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data['Expenses'], label='Previous Expenses')
    plt.plot(forecast_index, forecast, label='Forecasted Expenses', color='red')
    plt.xlabel('Date')
    plt.ylabel('Expenses')
    plt.title('Expense Forecast for Next 30 Days')
    plt.legend()

    # Save the plot to a file without displaying it
    plot_file = 'static/img/forecast_plot.png'
    plt.savefig(plot_file)
    plt.close()
    # Pass the data to the template
    context = {
        'forecast_data': forecast_data_list,
        'total_forecasted_expenses': total_forecasted_expenses,
        'category_forecasts': category_forecasts,
        'total_income': total_income,
        'total_expenses': total_expenses,
    }

    return render(request, 'expense_forecast/index.html', context)
