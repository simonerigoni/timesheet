from datetime import datetime, timedelta
from calendar import Calendar, HTMLCalendar
from .models import TimesheetDay, WorkingDay


class MonthCalendar(HTMLCalendar):
	def __init__(self, year = None, month = None):
		self.year = year
		self.month = month
		self.colors = {
			'WOD': 'LightCoral'
			, 'NWD' : 'LightSeaGreen'
            , 'WOH' : 'LightSalmon'
            , 'EWO' : 'LightPink'
            , 'VAC' : 'LightGreen'
            , 'PAR' : 'MediumAquaMarine'
            , 'CIG' : 'LightYellow'
            , 'IND' : 'LightSkyBlue'
            , 'SIC' : 'Orchid'
            , 'GPH' : 'Peru'
            , 'SMA' : 'PeachPuff'
        }
		super(MonthCalendar, self).__init__()

	def format_day(self, day, timesheetdays, workingdays):
		timesheetday = timesheetdays.filter(date__day = day)
		workingday = workingdays.filter(date__day = day)

		if len(timesheetday) > 0:
			timesheetday = timesheetday[0]

		if len(workingday) > 0:
			workingday = workingday[0]

		if day != 0:
			if timesheetday.is_working_day() == True:
				colore = self.colors[workingday.get_max_hours_type()[1]]
			else:
				colore = self.colors['NWD']
			return f'<td style="background-color:{colore}"><span class="date">{day}</span><ul><h2>{workingday.get_html_url()}</h2></ul></td>'
		else:
			return '<td></td>'

	def format_week(self, the_week, timesheetdays, workingdays):
		week = ''
		for d, weekday in the_week:
			week += self.format_day(d, timesheetdays, workingdays)
		return f'<tr> {week} </tr>'

	def format_month(self, with_year = True):
		timesheetdays = TimesheetDay.objects.filter(date__year = self.year, date__month = self.month)
		workingdays = WorkingDay.objects.filter(date__year = self.year, date__month = self.month)
		cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
		cal += f'{self.formatmonthname(self.year, self.month, withyear = with_year)}\n'
		cal += f'{self.formatweekheader()}\n'
		for week in self.monthdays2calendar(self.year, self.month):
			cal += f'{self.format_week(week, timesheetdays, workingdays)}\n'
		cal += f'</table'
		return cal


class YearCalendar(HTMLCalendar):
	def __init__(self, year = None):
		self.year = year
		self.colors = {
			'WOD': 'LightCoral'
			, 'NWD' : 'LightSeaGreen'
            , 'WOH' : 'LightSalmon'
            , 'EWO' : 'LightPink'
            , 'VAC' : 'LightGreen'
            , 'PAR' : 'MediumAquaMarine'
            , 'CIG' : 'LightYellow'
            , 'IND' : 'LightSkyBlue'
            , 'SIC' : 'Orchid'
            , 'GPH' : 'Peru'
            , 'SMA' : 'PeachPuff'
        }
		super(YearCalendar, self).__init__()

	def format_day(self, day, timesheetdays, workingdays):
		timesheetday = timesheetdays.filter(date__day = day)
		workingday = workingdays.filter(date__day = day)

		if len(timesheetday) > 0:
			timesheetday = timesheetday[0]

		if len(workingday) > 0:
			workingday = workingday[0]

		if timesheetday.is_working_day() == True:
			#colore = self.colors['WOD']
			colore = self.colors[workingday.get_max_hours_type()[1]]
		else:
			colore = self.colors['NWD']
		return f'<td style="background-color:{colore}"><span class="date"><h6>{timesheetday.get_html_url(human_readable = False)}</h6><h6>{workingday.get_max_hours_type()[0]} {workingday.get_max_hours_type()[1]}</h6></span></td>'


	def format_month(self, the_month, timesheetdays, workingdays):
		month = '<tr><td><span class="date"><a href="/month/?month={}-{}">{}</a></span></td>'.format(self.year, the_month, the_month)
		c = Calendar()
		count_days_31 = 0
		for d in c.itermonthdays(self.year, the_month):
			if d == 0:
				pass
			else:
				count_days_31 += 1
				month += self.format_day(d, timesheetdays, workingdays)
		for i in range(31 - count_days_31):
			month += f'<td><span class="date"></span></td>'
		return f'{month}</tr>'


	def format_year(self):
		cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
		cal += f'<h5 class = "text-center">{self.year}</h5>\n'
		cal += f'<tr><td><span class="date"></span></td><td><span class="date">1</span></td><td><span class="date">2</span></td><td><span class="date">3</span></td><td><span class="date">4</span></td><td><span class="date">5</span></td><td><span class="date">6</span></td><td><span class="date">7</span></td><td><span class="date">8</span></td><td><span class="date">9</span></td><td><span class="date">10</span></td><td><span class="date">11</span></td><td><span class="date">12</span></td><td><span class="date">13</span></td><td><span class="date">14</span></td><td><span class="date">15</span></td><td><span class="date">16</span></td><td><span class="date">17</span></td><td><span class="date">18</span></td><td><span class="date">19</span></td><td><span class="date">20</span></td><td><span class="date">21</span></td><td><span class="date">22</span></td><td><span class="date">23</span></td><td><span class="date">24</span></td><td><span class="date">25</span></td><td><span class="date">26</span></td><td><span class="date">27</span></td><td><span class="date">28</span></td><td><span class="date">29</span></td><td><span class="date">30</span></td><td><span class="date">31</span></td></tr>\n'

		for month in range(1, 13):
			timesheetdays = TimesheetDay.objects.filter(date__year = self.year, date__month = month)
			workingdays = WorkingDay.objects.filter(date__year = self.year, date__month = month)
			cal += f'{self.format_month(month, timesheetdays, workingdays)}\n'
		cal += f'</table'
		return cal