from datetime import date

import pytest

from timesheet.models import Paycheck, TimesheetDay, WorkingDay
from timesheet.views import get_date, next_month, next_year, prev_month, prev_year


@pytest.mark.django_db
def test_timesheetday_helpers():
    working = TimesheetDay.objects.create(date=date(2099, 1, 15), day_type="WOD")
    rest = TimesheetDay.objects.create(date=date(2099, 1, 16), day_type="NWD")
    assert working.is_working_day() is True
    assert rest.is_working_day() is False
    assert working.get_year() == 2099
    assert working.get_month() == 1
    assert working.get_human_readable_day_type()
    assert "WOD" in working.get_html_url(human_readable=False)
    assert "href=" in working.get_html_url(human_readable=True)


@pytest.mark.django_db
def test_workingday_hour_helpers():
    day = WorkingDay.objects.create(
        date=date(2099, 2, 3),
        office_working_hours=8,
        extra_time_working_hours=2,
        vacation_hours=0,
        par_hours=0,
        cigo_hours=0,
        mild_illness_hours=0,
        sick_leave_hours=0,
        generic_permit_hours=0,
        smartworking_hours=0,
        reduction_working_hours=0,
    )
    assert day.get_sum_hours() == 10
    assert day.get_year() == 2099
    assert day.get_month() == 2
    hours, hour_type = day.get_max_hours_type()
    assert hours == 8
    assert hour_type == "WOH"
    day.set_zero_hours()
    day.save()
    assert day.get_sum_hours() == 0


@pytest.mark.django_db
def test_paycheck_difference_and_date_helpers():
    paycheck = Paycheck.objects.create(
        date=date(2099, 3, 31),
        gross_salary=2000.0,
        net_salary=1500.55,
    )
    assert paycheck.difference_gross_net_salary == 499.45
    assert paycheck.get_year() == 2099
    assert paycheck.get_month() == 3
    assert "paycheck" in paycheck.get_html_url()


def test_get_date_and_navigation_helpers():
    assert get_date("2020-4") == date(2020, 4, 1)
    assert get_date("2021") == date(2021, 1, 1)
    current = date(2020, 1, 15)
    assert prev_month(current) == "month=2019-12"
    assert next_month(current) == "month=2020-2"
    assert prev_year(current) == "year=2019"
    assert next_year(current) == "year=2021"
    assert get_date("").year  # falls back to today
