from django.shortcuts import render
from django.http import HttpResponse
import csv
import io
import pandas as pd
from django.contrib.auth.decorators import login_required
from expenses.models import Expense
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
import datetime
import openpyxl
from xhtml2pdf import pisa

@login_required(login_url='/authentication/login')
def income_expense_report(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        start_date_parsed = parse_date(start_date)
        end_date_parsed = parse_date(end_date)

        expenses = Expense.objects.filter(owner=request.user, date__range=[start_date_parsed, end_date_parsed])

        context = {
            'expenses': expenses,
            'start_date': start_date,
            'end_date': end_date,
        }
        return render(request, 'report_generation/report.html', context)
    else:
        return render(request, 'report_generation/report.html')

@login_required(login_url='/authentication/login')
def export_csv(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    start_date_parsed = parse_date(start_date)
    end_date_parsed = parse_date(end_date)

    expenses = Expense.objects.filter(owner=request.user, date__range=[start_date_parsed, end_date_parsed])

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="income_expense_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Category', 'Description', 'Amount'])

    for expense in expenses:
        writer.writerow([expense.date, expense.category, expense.description, expense.amount])

    return response

@login_required(login_url='/authentication/login')
def export_xlsx(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    start_date_parsed = parse_date(start_date)
    end_date_parsed = parse_date(end_date)

    expenses = Expense.objects.filter(owner=request.user, date__range=[start_date_parsed, end_date_parsed])

    output = io.BytesIO()
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Income Expense Report'

    headers = ['Date', 'Category', 'Description', 'Amount']
    sheet.append(headers)

    for expense in expenses:
        sheet.append([expense.date, expense.category, expense.description, expense.amount])

    workbook.save(output)
    output.seek(0)

    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=income_expense_report.xlsx'
    return response

@login_required(login_url='/authentication/login')
def export_pdf(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    start_date_parsed = parse_date(start_date)
    end_date_parsed = parse_date(end_date)

    expenses = Expense.objects.filter(owner=request.user, date__range=[start_date_parsed, end_date_parsed])

    context = {
        'expenses': expenses,
        'start_date': start_date,
        'end_date': end_date,
    }

    html_string = render_to_string('report_generation/report_pdf.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="income_expense_report.pdf"'

    pisa_status = pisa.CreatePDF(html_string, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html_string + '</pre>')
    return response
