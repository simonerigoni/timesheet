from django.forms import ModelForm, DateInput
from .models import TimesheetDay, WorkingDay, Paycheck

class TimesheetDayForm(ModelForm):
  class Meta:
    model = TimesheetDay
    # datetime-local is a HTML5 input type, format to make date time show on fields
    widgets = {
      'date': DateInput(attrs={'type': 'date-local'}, format='%Y-%m-%d'),
    }
    fields = '__all__'

  def __init__(self, *args, **kwargs):
    super(TimesheetDayForm, self).__init__(*args, **kwargs)
    # input_formats parses HTML5 datetime-local input to datetime field
    self.fields['date'].input_formats = ('%Y-%m-%d',)
    self.fields['date'].widget.attrs['readonly'] = True


class WorkingDayForm(ModelForm):
  class Meta:
    model = WorkingDay
    # datetime-local is a HTML5 input type, format to make date time show on fields
    widgets = {
      'date': DateInput(attrs={'type': 'date-local'}, format='%Y-%m-%d'),
    }
    fields = '__all__'

  def __init__(self, *args, **kwargs):
    super(WorkingDayForm, self).__init__(*args, **kwargs)
    # input_formats parses HTML5 datetime-local input to datetime field
    self.fields['date'].input_formats = ('%Y-%m-%d',)
    self.fields['date'].widget.attrs['readonly'] = True

  def clean(self):
    cleaned_data = super().clean()

    try:
        hours_sum = (
            cleaned_data['office_working_hours']
            + cleaned_data['vacation_hours']
            + cleaned_data['par_hours']
            + cleaned_data['cigo_hours']
            + cleaned_data['mild_illness_hours']
            + cleaned_data['sick_leave_hours']
            + cleaned_data['generic_permit_hours']
            + cleaned_data['smartworking_hours']
        )
    except KeyError:
        pass
    else:
        if hours_sum != 8:
            self.add_error(
                None,
                (
                    f"Non Extra Time Working Hours must add up to 8, they currently add up to {hours_sum}"
                )
            )

    return cleaned_data


class PaycheckForm(ModelForm):
  class Meta:
    model = Paycheck
    # datetime-local is a HTML5 input type, format to make date time show on fields
    widgets = {
      'date': DateInput(attrs={'type': 'date-local'}, format='%Y-%m-%d'),
    }
    fields = '__all__'

  def __init__(self, *args, **kwargs):
    super(PaycheckForm, self).__init__(*args, **kwargs)
    # input_formats parses HTML5 datetime-local input to datetime field
    self.fields['date'].input_formats = ('%Y-%m-%d',)
    self.fields['date'].widget.attrs['readonly'] = True