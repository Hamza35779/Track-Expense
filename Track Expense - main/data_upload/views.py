import csv
import io
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from expenses.models import Expense
from userincome.models import UserIncome
from django.db import transaction

@login_required(login_url='/authentication/login')
def upload_csv(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('file')
        if not csv_file:
            messages.error(request, 'No file selected')
            return redirect('upload-csv')

        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'File is not CSV type')
            return redirect('upload-csv')

        try:
            data_set = csv_file.read().decode('UTF-8')
            io_string = io.StringIO(data_set)
            reader = csv.DictReader(io_string)

            with transaction.atomic():
                for row in reader:
                    # Assuming CSV has columns: type, date, description, amount, category/source
                    # type: 'expense' or 'income'
                    record_type = row.get('type', '').strip().lower()
                    date = row.get('date', '').strip()
                    description = row.get('description', '').strip()
                    amount = float(row.get('amount', 0))
                    category_or_source = row.get('category', '').strip()

                    if record_type == 'expense':
                        Expense.objects.create(
                            owner=request.user,
                            date=date,
                            description=description,
                            amount=amount,
                            category=category_or_source
                        )
                    elif record_type == 'income':
                        UserIncome.objects.create(
                            owner=request.user,
                            date=date,
                            description=description,
                            amount=amount,
                            source=category_or_source
                        )
            messages.success(request, 'CSV file processed successfully')
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f'Error processing file: {str(e)}')
            return redirect('upload-csv')

    return render(request, 'data_upload/upload_csv.html')
