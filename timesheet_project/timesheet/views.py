from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.views import generic
from django.urls import reverse
from django.utils.safestring import mark_safe
import calendar
from datetime import datetime, timedelta, date

from .models import TimesheetDay, WorkingDay, Paycheck
from .utils import MonthCalendar, YearCalendar
from .forms import TimesheetDayForm, WorkingDayForm, PaycheckForm

import holidays
import json

def get_date(req):
    if req:
        if '-' in req:
            year, month = (int(x) for x in req.split('-'))
            return date(year, month, day = 1)
        else:
            year = int(req)
            return date(year, month = 1, day = 1)
    else:
        return datetime.today()


def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days = 1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month


def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day = days_in_month)
    next_month = last + timedelta(days = 1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month


def prev_year(d):
    return 'year=' + str(d.year - 1) 


def next_year(d):
    return 'year=' + str(d.year + 1) 

def get_years_from_timesheetdays():
    timesheetdays = TimesheetDay.objects.all()
    years = []
    for timesheetday in timesheetdays:
        years.append(timesheetday.get_year())
    return list(set(years))


def get_day_data(filter_year):
    day_data = dict()
    timesheetdays = TimesheetDay.objects.filter(date__year__in = filter_year)
    count_working_day = 0
    count_non_working_day = 0

    for timesheetday in timesheetdays:
        if timesheetday.is_working_day() == True:
            count_working_day += 1
        else:
            count_non_working_day += 1

    day_data['Working Day'] = (count_working_day, count_working_day * 8)
    day_data['Non Working Day'] = (count_non_working_day, count_non_working_day * 8)
    day_data['Total'] = (count_working_day + count_non_working_day, (count_working_day + count_non_working_day) * 8)
    return day_data


def get_hour_data(filter_year):
    hour_data = dict()
    workingdays = WorkingDay.objects.filter(date__year__in = filter_year)
    count_office_working_hours = 0
    count_extra_time_working_hours = 0
    count_vacation_hours = 0
    count_par_hours = 0
    count_cigo_hours = 0
    count_mild_illness_hours = 0
    count_sick_leave_hours = 0
    count_generic_permit_hours = 0
    count_smartworking_hours = 0

    for workingday in workingdays:
        count_office_working_hours += workingday.office_working_hours
        count_extra_time_working_hours += workingday.extra_time_working_hours
        count_vacation_hours += workingday.vacation_hours
        count_par_hours += workingday.par_hours
        count_cigo_hours += workingday.cigo_hours
        count_mild_illness_hours += workingday.mild_illness_hours
        count_sick_leave_hours += workingday.sick_leave_hours
        count_generic_permit_hours += workingday.generic_permit_hours
        count_smartworking_hours += workingday.smartworking_hours
    
    hour_data['Office Working Hours'] = count_office_working_hours
    hour_data['Extra Time Working Hours'] = count_extra_time_working_hours
    hour_data['Vacation hours'] = count_vacation_hours
    hour_data['PAR Hours'] = count_par_hours
    hour_data['CIGO Hours'] = count_cigo_hours
    hour_data['Mild Illness Hours'] = count_mild_illness_hours
    hour_data['Sick Leave Hours'] = count_sick_leave_hours
    hour_data['Generic Permit Hours'] = count_generic_permit_hours
    hour_data['Smartworking Hours'] = count_smartworking_hours
    hour_data['Total'] = count_office_working_hours + count_extra_time_working_hours + count_vacation_hours + count_par_hours + count_cigo_hours + count_mild_illness_hours + count_sick_leave_hours + count_generic_permit_hours + count_smartworking_hours
    return hour_data


def get_paycheck_data(filter_year):
    paycheck_data = dict()
    sum_gross_salary = 0
    sum_net_salary = 0
    sum_difference_gross_net_salary = 0
    count = 0

    for month in range(1, 13):
        paychecks = Paycheck.objects.filter(date__year__in = filter_year, date__month = month)
        for paycheck in paychecks:
            paycheck_data[paycheck.id] = (0, month, paycheck.gross_salary, paycheck.net_salary, paycheck.difference_gross_net_salary)

    #print(paycheck_data)

    if len(filter_year) > 1:
        agg_paycheck_data = dict()
        #print(paycheck_data.keys())
        for k in paycheck_data.keys():
            _, month, gross, net, diff = paycheck_data[k]
            if month not in agg_paycheck_data.keys():
                agg_paycheck_data[month] = (gross, net, diff)
            else:
                current = agg_paycheck_data[month]
                agg_paycheck_data[month] = (current[0] + gross, current[1] + net, current[2] + diff)
        #print(agg_paycheck_data)

        temp_paycheck_data = dict()
        for k in agg_paycheck_data.keys():
            gross, net, diff = agg_paycheck_data[k]
            temp_paycheck_data[k] = (2, k, round(gross, 2), round(net, 2), round(diff, 2))
        paycheck_data = temp_paycheck_data

    for k in paycheck_data.keys():
        _, month, gross, net, diff = paycheck_data[k]
        if (gross + net + diff) == 0:
            pass
        else:
            sum_gross_salary += gross
            sum_net_salary += net
            sum_difference_gross_net_salary += diff
            count += 1
    paycheck_data['Total'] = (1, 0, round(sum_gross_salary, 2), round(sum_net_salary, 2), round(sum_difference_gross_net_salary, 2))
    if count == 0:
        paycheck_data['Average'] = (1, 0, 0, 0, 0)
    else:
        paycheck_data['Average'] = (1, 0, round(sum_gross_salary / count, 2), round(sum_net_salary / count, 2), round(sum_difference_gross_net_salary / count, 2))

    #print(paycheck_data)

    return paycheck_data


# Create your views here.

def timesheet(request):
    years = get_years_from_timesheetdays()

    if len(years) > 0:
        if datetime.now().year in years:
            filter_year = [(datetime.now().year)]
        else:
            filter_year = [(years[0])]
    else:
        filter_year = []

    if request.method == 'POST':
        if 'year-button-filter' in request.POST:
            #print(request.POST.getlist('year-input-filter'))
            filter_year = [int(y) for y in request.POST.getlist('year-input-filter')]
        else:
            input_year = request.POST.get('year-input-add-delete', 0)
            if input_year == '':
                input_year = 0
            else:
                input_year = int(input_year)
            if input_year == 0:
                pass
            else:
                if 'year-button-delete' in request.POST:
                    timesheetdays = TimesheetDay.objects.filter(date__year = input_year)
                    for timesheetday in timesheetdays:
                        if timesheetday.get_year() == input_year:
                            timesheetday.delete()
                    workingdays = WorkingDay.objects.filter(date__year = input_year)
                    for workingday in workingdays:
                        if workingday.get_year() == input_year:
                            workingday.delete()
                    paychecks = Paycheck.objects.filter(date__year = input_year)
                    for paycheck in paychecks:
                        paycheck.delete()
                elif 'year-button-add' in request.POST:
                    if input_year not in years:
                        cal = MonthCalendar(input_year)
                        vacanze = holidays.Italy(years = input_year).items()
                        vacanze = [data[0] for data in vacanze]
                        vacanze.append(date(input_year, 12, 7)) #Sant'Ambrogio Patrono di Milano

                        for quarter in (cal.yeardatescalendar(input_year)):
                            for month in quarter:
                                for week in month:
                                    for day in week:
                                        if day.year == input_year:
                                            timesheetdays = TimesheetDay.objects.all()
                                            dates = []
                                            workingday = None
                                            for timesheetday in timesheetdays:
                                                dates.append(timesheetday.date)
                                            dates = list(set(dates))
                                            if day in dates:
                                                pass
                                            else:
                                                if day in vacanze:
                                                    timesheetday = TimesheetDay(day_type = 'NWD', date = day)
                                                    workingday = WorkingDay(date = day, office_working_hours = 0, extra_time_working_hours = 0, vacation_hours = 0, par_hours = 0, cigo_hours = 0, mild_illness_hours = 0, sick_leave_hours = 0, generic_permit_hours = 0, smartworking_hours = 0)
                                                else:
                                                    if calendar.weekday(day.year, day.month, day.day) == 5 or calendar.weekday(day.year, day.month, day.day) == 6: # Saturdday or Sunday
                                                        timesheetday = TimesheetDay(day_type = 'NWD', date = day)
                                                        workingday = WorkingDay(date = day, office_working_hours = 0, extra_time_working_hours = 0, vacation_hours = 0, par_hours = 0, cigo_hours = 0, mild_illness_hours = 0, sick_leave_hours = 0, generic_permit_hours = 0, smartworking_hours = 0)
                                                    else:
                                                        timesheetday = TimesheetDay(day_type = 'WOD', date = day)
                                                        workingday = WorkingDay(date = day, office_working_hours = 8, extra_time_working_hours = 0, vacation_hours = 0, par_hours = 0, cigo_hours = 0, mild_illness_hours = 0, sick_leave_hours = 0, generic_permit_hours = 0, smartworking_hours = 0)

                                                if timesheetday == None:
                                                    pass
                                                else:
                                                    timesheetday.save()
                                                if workingday == None:
                                                    pass
                                                else:
                                                    workingday.save()

                        for month in range(1, 13):
                            paycheck = Paycheck(date = datetime(input_year, month, 27))
                            paycheck.save()


    years = get_years_from_timesheetdays()

    day_data = get_day_data(filter_year)

    hour_data = get_hour_data(filter_year)

    paycheck_data = get_paycheck_data(filter_year)

    hour_data_labels = list(hour_data.keys())[:-1] # remove last element wich is the Total
    hour_data_data = [hour_data[k] for k in hour_data.keys()][:-1] # remove last element wich is the Total

    paycheck_data_labels = []
    paycheck_data_data = []

    for k in paycheck_data.keys():
        _, month, gross, net, diff = paycheck_data[k]
        paycheck_data_labels.append(month)
        paycheck_data_data.append(net)

    paycheck_data_labels = paycheck_data_labels[:-2]
    paycheck_data_data = paycheck_data_data[:-2]

    # massive updats
    # pippos = TimesheetDay.objects.filter(date__year = 2017)
    # for pippo in pippos:
    #     if pippo.date < date(2017, 10, 2):
    #         pippo.day_type = 'NWD'
    #         pippo.save()
    #         paperino = WorkingDay.objects.filter(date = pippo.date)
    #         if len(paperino) > 0:
    #             paperino = paperino[0]

    #         paperino.set_zero_hours()
    #         paperino.save() 
    #

    return render(request, template_name = 'timesheet/timesheet.html', context = {'filter_year':filter_year, 'years':years, 'day_data':day_data, 'hour_data':hour_data, 'paycheck_data':paycheck_data, 'hour_data_labels': json.dumps(hour_data_labels), 'hour_data_data': json.dumps(hour_data_data), 'paycheck_data_labels': json.dumps(paycheck_data_labels), 'paycheck_data_data': json.dumps(paycheck_data_data),})


def year(request):
    return render(request, 'timesheet/year.html', {})


class MonthView(generic.ListView):
    model = TimesheetDay
    template_name = 'timesheet/month.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get('month', None))
        cal = MonthCalendar(d.year, d.month)
        html_cal = cal.format_month(with_year = True)
        context['calendar'] = mark_safe(html_cal)
        context['year'] = d.year
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        return context


class YearView(generic.ListView):
    model = TimesheetDay
    template_name = 'timesheet/year.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get('year', None))
        cal = YearCalendar(d.year)
        html_cal = cal.format_year()
        context['calendar'] = mark_safe(html_cal)
        context['prev_year'] = prev_year(d)
        context['next_year'] = next_year(d)
        return context


def timesheetday(request, timesheetday_id):
    if timesheetday_id:
        timesheetday = get_object_or_404(TimesheetDay, pk = timesheetday_id)
        timesheetday_prev_day_type = timesheetday.day_type
    else:
        timesheetday = TimesheetDay()

    form = TimesheetDayForm(request.POST or None, instance = timesheetday)
    if request.POST and form.is_valid():
        form.save()
        timesheetday = get_object_or_404(TimesheetDay, pk = timesheetday_id)
        if timesheetday.day_type == timesheetday_prev_day_type:
            pass
        else:
            workingday = WorkingDay.objects.filter(date = timesheetday.date)
            if len(workingday) > 0:
                workingday = workingday[0]

            if timesheetday.day_type == 'WOD':
                workingday.office_working_hours = 8
            else:
                workingday.set_zero_hours()
            #print(workingday)
            workingday.save()    

        return HttpResponseRedirect('/year/?year=' + str(timesheetday.get_year()))

    return render(request, 'timesheet/form.html', {'form': form})


def workingday(request, workingday_id):
    if workingday_id:
        workingday = get_object_or_404(WorkingDay, pk = workingday_id)
    else:
        workingday = WorkingDay()

    form = WorkingDayForm(request.POST or None, instance = workingday)
    if request.POST and form.is_valid():
        form.save()
        return HttpResponseRedirect('/month/?month=' + str(workingday.get_year()) + '-' + str(workingday.get_month()))

    return render(request, 'timesheet/form.html', {'form': form})


def paycheck(request, paycheck_id):
    if paycheck_id:
        paycheck = get_object_or_404(Paycheck, pk = paycheck_id)
    else:
        paycheck = Paycheck()

    form = PaycheckForm(request.POST or None, instance = paycheck)
    if request.POST and form.is_valid():
        form.save()
        return HttpResponseRedirect('/')

    return render(request, 'timesheet/form.html', {'form': form})


def massive_edit(request):
    init_start_date_input = date.today().strftime('%Y-%m-%d')
    init_end_date_input = date.today().strftime('%Y-%m-%d')
    submitted = 0
    type_day = 0
    if request.method == 'POST':
        if 'Timesheet Day' in request.POST.get('type-input-filter', ''):
            type_day = 1
            pass
        elif 'Working Day' in request.POST.get('type-input-filter', ''):
            type_day = 2
        else:
            start_date = datetime.strptime(request.POST['start-date-input'], '%Y-%m-%d').date()
            end_date = datetime.strptime(request.POST['end-date-input'], '%Y-%m-%d').date()
            # print(start_date)
            # print(end_date)
            timesheetdays = TimesheetDay.objects.filter(date__range = [start_date, end_date])
            workingdays = WorkingDay.objects.filter(date__range = [start_date, end_date])
            if start_date <= end_date:
                if ('Non Working Day' in request.POST.get('timesheet-day-input', '')) or ('Working Day' in request.POST.get('timesheet-day-input', '')):
                    for timesheetday in timesheetdays:
                        workingday = workingdays.filter(date = timesheetday.date)
                        if len(workingday) > 0:
                            workingday = workingday[0]
                        if 'Non Working Day' in request.POST.get('timesheet-day-input', ''):
                            timesheetday.day_type = 'NWD'
                            workingday.set_zero_hours()
                        else:
                            timesheetday.day_type = 'WOD'
                            workingday.office_working_hours = 8
                        workingday.save()
                        timesheetday.save()
                        #print(workingday.date)
                    submitted = 1
                elif ('Working Hours' in request.POST.get('working-day-input', '')) or ('Vacation Hours' in request.POST.get('working-day-input', '')) or ('PAR Hours' in request.POST.get('working-day-input', '')) or ('CIGO Hours' in request.POST.get('working-day-input', '')) or ('Mild Illness Hours' in request.POST.get('working-day-input', '')) or ('Sick Leave Hours' in request.POST.get('working-day-input', '')) or ('Generic Permit Hours' in request.POST.get('working-day-input', '')) or ('Smartworking Hours' in request.POST.get('working-day-input', '')):
                    for workingday in workingdays:
                        timesheetday = timesheetdays.filter(date = workingday.date)
                        if len(timesheetday) > 0:
                            timesheetday = timesheetday[0]
                        if timesheetday.day_type == 'WOD':
                            workingday.set_zero_hours()
                            if 'Working Hours' in request.POST.get('working-day-input', ''):
                                workingday.office_working_hours = 8
                            elif 'Vacation Hours' in request.POST.get('working-day-input', ''):
                                workingday.vacation_hours = 8
                            elif 'PAR Hours' in request.POST.get('working-day-input', ''):
                                workingday.par_hours = 8
                            elif 'CIGO Hours' in request.POST.get('working-day-input', ''):
                                workingday.cigo_hours = 8
                            elif 'Mild Illness Hours' in request.POST.get('working-day-input', ''):
                                workingday.mild_illness_hours = 8
                            elif 'Sick Leave Hours' in request.POST.get('working-day-input', ''):
                                workingday.sick_leave_hours = 8
                            elif 'Generic Permit Hours' in request.POST.get('working-day-input', ''):
                                workingday.generic_permit_hours = 8
                            else: #'Smartworking Hours' in request.POST.get('working-day-input', ''):
                                 workingday.smartworking_hours = 8
                            workingday.save()
                            #print(workingday.date)
                    submitted = 1
            else:
                submitted = 2
    # if paycheck_id:
    #     paycheck = get_object_or_404(Paycheck, pk = paycheck_id)
    # else:
    #     paycheck = Paycheck()

    # form = PaycheckForm(request.POST or None, instance = paycheck)
    # if request.POST and form.is_valid():
    #     form.save()
    #     return HttpResponseRedirect('/')

    return render(request, 'timesheet/massive_edit.html', {'type_day':type_day, 'submitted':submitted, 'init_start_date_input':init_start_date_input, 'init_end_date_input':init_end_date_input})