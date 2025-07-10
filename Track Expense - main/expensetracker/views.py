from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def root_redirect(request):
    return HttpResponseRedirect('/preferences/')

from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils.timezone import now, timedelta
from userincome.models import UserIncome
from expenses.models import Expense

@login_required(login_url='/authentication/login')
def dashboard(request):
    user = request.user
    today = now().date()
    start_week = today - timedelta(days=today.weekday())
    start_month = today.replace(day=1)
    start_year = today.replace(month=1, day=1)

    # Earnings calculations
    earnings_daily = UserIncome.objects.filter(owner=user, date=today).aggregate(total=Sum('amount'))['total'] or 0
    earnings_weekly = UserIncome.objects.filter(owner=user, date__gte=start_week).aggregate(total=Sum('amount'))['total'] or 0
    earnings_monthly = UserIncome.objects.filter(owner=user, date__gte=start_month).aggregate(total=Sum('amount'))['total'] or 0
    earnings_yearly = UserIncome.objects.filter(owner=user, date__gte=start_year).aggregate(total=Sum('amount'))['total'] or 0

    # Expense calculations
    expenses_daily = Expense.objects.filter(owner=user, date=today).aggregate(total=Sum('amount'))['total'] or 0
    expenses_weekly = Expense.objects.filter(owner=user, date__gte=start_week).aggregate(total=Sum('amount'))['total'] or 0
    expenses_monthly = Expense.objects.filter(owner=user, date__gte=start_month).aggregate(total=Sum('amount'))['total'] or 0
    expenses_yearly = Expense.objects.filter(owner=user, date__gte=start_year).aggregate(total=Sum('amount'))['total'] or 0

    # Savings calculations
    savings_daily = earnings_daily - expenses_daily
    savings_weekly = earnings_weekly - expenses_weekly
    savings_monthly = earnings_monthly - expenses_monthly
    savings_yearly = earnings_yearly - expenses_yearly

    # Earnings overview for last 12 months
    earnings_overview = []
    expenses_overview = []
    savings_overview = []
    for i in range(12):
        month_date = start_month - timedelta(days=30*i)
        month_start = month_date.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        total_earnings = UserIncome.objects.filter(owner=user, date__gte=month_start, date__lte=month_end).aggregate(total=Sum('amount'))['total'] or 0
        total_expenses = Expense.objects.filter(owner=user, date__gte=month_start, date__lte=month_end).aggregate(total=Sum('amount'))['total'] or 0
        earnings_overview.append({'month': month_start.strftime('%b'), 'amount': total_earnings})
        expenses_overview.append({'month': month_start.strftime('%b'), 'amount': total_expenses})
        savings_overview.append({'month': month_start.strftime('%b'), 'amount': total_earnings - total_expenses})
    earnings_overview.reverse()
    expenses_overview.reverse()
    savings_overview.reverse()

    # Revenue sources - count of income sources by name
    revenue_sources_qs = UserIncome.objects.filter(owner=user).values('source').annotate(total=Sum('amount'))
    revenue_sources = {item['source']: item['total'] for item in revenue_sources_qs}

    context = {
        'earnings_daily': earnings_daily,
        'earnings_weekly': earnings_weekly,
        'earnings_monthly': earnings_monthly,
        'earnings_yearly': earnings_yearly,
        'expenses_daily': expenses_daily,
        'expenses_weekly': expenses_weekly,
        'expenses_monthly': expenses_monthly,
        'expenses_yearly': expenses_yearly,
        'savings_daily': savings_daily,
        'savings_weekly': savings_weekly,
        'savings_monthly': savings_monthly,
        'savings_yearly': savings_yearly,
        'earnings_overview': earnings_overview,
        'expenses_overview': expenses_overview,
        'savings_overview': savings_overview,
        'revenue_sources': revenue_sources,
    }
    # Replace any currency symbol with "Rs." in string values in context
    currency_symbols = ['₹', '$', '€', '£', '¥']
    for key, value in context.items():
        if isinstance(value, str):
            for symbol in currency_symbols:
                value = value.replace(symbol, 'Rs.')
            context[key] = value
    # Also replace currency symbols in earnings_overview, expenses_overview, savings_overview amounts if present
    for overview in ['earnings_overview', 'expenses_overview', 'savings_overview']:
        for item in context[overview]:
            if isinstance(item['amount'], str):
                for symbol in currency_symbols:
                    item['amount'] = item['amount'].replace(symbol, 'Rs.')
            # Sanitize any string fields in the item dict for ₹ symbol
            for key, val in item.items():
                if isinstance(val, str):
                    for symbol in currency_symbols:
                        item[key] = val.replace(symbol, 'Rs.')
    return render(request, 'dashboard.html', context)
