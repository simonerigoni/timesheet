from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse

# Create your models here.

class TimesheetDay(models.Model):
    DAY_TYPES = [
        ('WOD', 'Working Day'),
        ('NWD', 'Non Working Day')
    ]
    day_type = models.CharField(max_length = 3, choices = DAY_TYPES, default = 'WOD')
    date = models.DateField()
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields = ['day_type', 'date'], name = 'unique_timesheetday_day_type_date'),
        ]

    def get_human_readable_day_type(self):
        dict_day_types = dict(self.DAY_TYPES)
        return dict_day_types[self.day_type]

    def is_working_day(self):
        if self.day_type == 'WOD':
            return True
        else:
            return False

    def get_year(self):
        return self.date.year

    def get_month(self):
        return self.date.month

    def get_html_url(self, human_readable = True):
        url = reverse('timesheetday_edit', args = (self.id, ))
        if human_readable == True:
            return f'<a href="{url}">{self.get_human_readable_day_type()}</a>'
        else:
            return f'<a href="{url}">{self.day_type}</a>'


class WorkingDay(models.Model):
    HOURS_TYPES = [
        ('WOH', 'Office Working Hours'),
        ('EWO', 'Extra Working Hours'),
        ('VAC', 'Vacation Hours'),
        ('PAR', 'PAR Hours'),
        ('CIG', 'CIGO Hours'),
        ('IND', 'Mild Illness Hours'),
        ('SIC', 'Sick Leave Hours'),
        ('GPH', 'Generic Permit Hours'),
        ('SMA', 'Smartworking Hours'),
        ('RWH', 'Reduction of Working Hours')
    ]
    date = models.DateField() #models.ForeignKey(TimesheetDay, on_delete = models.CASCADE)
    office_working_hours = models.IntegerField(default = 8, validators = [MinValueValidator(0), MaxValueValidator(8)])
    extra_time_working_hours = models.IntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(8)])
    vacation_hours = models.PositiveIntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(8)])
    par_hours = models.PositiveIntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(8)])
    cigo_hours = models.PositiveIntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(8)])
    mild_illness_hours = models.PositiveIntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(8)])
    sick_leave_hours = models.PositiveIntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(8)])
    generic_permit_hours = models.PositiveIntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(8)])
    smartworking_hours = models.PositiveIntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(8)])
    reduction_working_hours = models.PositiveIntegerField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(8)])

    def get_year(self):
        return self.date.year

    def get_month(self):
        return self.date.month

    def set_zero_hours(self):
        self.office_working_hours = 0
        self.extra_time_working_hours = 0
        self.vacation_hours = 0
        self.par_hours = 0
        self.cigo_hours = 0
        self.mild_illness_hours = 0
        self.sick_leave_hours = 0
        self.generic_permit_hours = 0
        self.smartworking_hours = 0
        self.reduction_working_hours = 0

    def get_sum_hours(self):
        return self.office_working_hours + self.extra_time_working_hours + self.vacation_hours + self.par_hours + self.cigo_hours + self.mild_illness_hours + self.sick_leave_hours + self.generic_permit_hours + self.smartworking_hours + self.reduction_working_hours
    
    def get_max_hours_type(self):
        dict_var = {
            'WOH' : self.office_working_hours
            , 'EWO' : self.extra_time_working_hours
            , 'VAC' : self.vacation_hours
            , 'PAR' : self.par_hours
            , 'CIG' : self.cigo_hours
            , 'IND' : self.mild_illness_hours
            , 'SIC' : self.sick_leave_hours
            , 'GPH' : self.generic_permit_hours
            , 'SMA' : self.smartworking_hours
            , 'RWH' : self.reduction_working_hours
        }
        max = 0
        max_hours_type = ''
        for var in dict_var.keys():
            if dict_var[var] > max:
                max = dict_var[var]
                max_hours_type = var
        if max == 0:
            return ('', '')
        else:
            return (max, max_hours_type)

    def get_non_zero_hours(self):
        stringa = ''
        dict_var = {
            'WOH' : self.office_working_hours
            , 'EWO' : self.extra_time_working_hours
            , 'VAC' : self.vacation_hours
            , 'PAR' : self.par_hours
            , 'CIG' : self.cigo_hours
            , 'IND' : self.mild_illness_hours
            , 'SIC' : self.sick_leave_hours
            , 'GPH' : self.generic_permit_hours
            , 'SMA' : self.smartworking_hours
            , 'RWH' : self.reduction_working_hours
        }
        for var in dict_var.keys():
            if dict_var[var] > 0:
                stringa += '{} {} + '.format(dict_var[var], var)
        
        stringa = stringa.strip(' + ')
        return stringa

    def get_human_readable_hour_type(self, hour_type):
        dict_hour_types = dict(self.HOURS_TYPES)
        return dict_hour_types[hour_type]

    def get_html_url(self):
        url = reverse('workingday_edit', args = (self.id, ))
        stringa = self.get_non_zero_hours()

        return f'<a href="{url}">{stringa}</a>'

    # class Meta:
    #     constraints = [
    #         models.CheckConstraint(check = models.Q(
    #                                                 office_working_hours = (
    #                                                     8
    #                                                     - models.F('vacation_hours')
    #                                                     - models.F('par_hours')
    #                                                     - models.F('cigo_hours')
    #                                                     - models.F('mild_illness_hours')
    #                                                     - models.F('sick_leave_hours')
    #                                                     - models.F('generic_permit_hours')
    #                                                     - models.F('smartworking_hours')
    #                                                     - models.F('reduction_working_hours')
    #                                                 )
    #                                             ),
    #                             name = 'workingday_hours_sum_8')

    #     ]


class Paycheck(models.Model):
    date = models.DateField() # models.ForeignKey(TimesheetDay, on_delete = models.CASCADE)
    gross_salary = models.FloatField(default = 0.0, validators = [MinValueValidator(0.0), MaxValueValidator(9999.99)])
    net_salary = models.FloatField(default = 0.0, validators = [MinValueValidator(0.0), MaxValueValidator(9999.99)])
    payslip = models.FileField(upload_to = 'timesheet/paycheck/payslips/', null = True, blank = True)
    
    @property
    def difference_gross_net_salary(self):
        return round(self.gross_salary - self.net_salary, 2)

    def get_year(self):
        return self.date.year

    def get_month(self):
        return self.date.month

    def get_html_url(self):
        url = reverse('paycheck_edit', args = (self.id, ))
        return f'<a href="{url}"> {self.get_month()}</a>'
