"""timesheet_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path

import home.views
import hello_world.views
import timesheet.views


urlpatterns = [
    path('admin/', admin.site.urls),
    #path('',  home.views.welcome, name = 'home'),
    #path('hello_world/',  hello_world.views.hello_world, name = 'hello_world'),
    path('',  timesheet.views.timesheet, name = 'home'),
    path('month/',  timesheet.views.MonthView.as_view(), name = 'month'),
    path('year/',  timesheet.views.YearView.as_view(), name = 'year'),
    path('timesheetday/edit/<int:timesheetday_id>/', timesheet.views.timesheetday, name = 'timesheetday_edit'),
    path('workingday/edit/<int:workingday_id>/', timesheet.views.workingday, name = 'workingday_edit'),
    path('paycheck/edit/<int:paycheck_id>/', timesheet.views.paycheck, name = 'paycheck_edit'),
    path('massive_edit/', timesheet.views.massive_edit, name = 'massive_edit'),
]
