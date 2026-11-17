from calendar import monthrange
from datetime import date

import pytest
from django.test import Client

from timesheet.models import TimesheetDay, WorkingDay
from timesheet.utils import MonthCalendar, YearCalendar


def _seed_month(year, month, day_type="NWD"):
    last = monthrange(year, month)[1]
    for day in range(1, last + 1):
        TimesheetDay.objects.create(date=date(year, month, day), day_type=day_type)
        WorkingDay.objects.create(date=date(year, month, day), office_working_hours=0)


def _seed_year(year, day_type="NWD"):
    for month in range(1, 13):
        _seed_month(year, month, day_type=day_type)


@pytest.mark.django_db
def test_month_calendar_html_closes_table():
    _seed_month(2099, 1, day_type="NWD")
    html = MonthCalendar(2099, 1).format_month()
    assert html.strip().endswith("</table>")
    assert "</table" in html
    assert "<table" in html
    assert "calendar" in html


@pytest.mark.django_db
def test_year_calendar_html_closes_table():
    _seed_year(2099, day_type="NWD")
    html = YearCalendar(2099).format_year()
    assert html.strip().endswith("</table>")
    assert "<table" in html
    assert "2099" in html
    assert "/month/?month=2099-1" in html


@pytest.mark.django_db
def test_month_and_year_views_render(client: Client):
    _seed_year(2099, day_type="NWD")
    month_response = client.get("/month/?month=2099-1")
    assert month_response.status_code == 200
    assert b"</table>" in month_response.content
    year_response = client.get("/year/?year=2099")
    assert year_response.status_code == 200
    assert b"</table>" in year_response.content


@pytest.mark.django_db
def test_home_view_renders():
    response = Client().get("/")
    assert response.status_code == 200
