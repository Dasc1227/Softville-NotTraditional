from datetime import datetime, timedelta
from django import forms
from django.utils.translation import gettext_lazy as _

from appointments.models import Appointment


class RegisterAppointmentForm(forms.ModelForm):
    date = forms.DateField(label="Fecha", widget=forms.DateInput(attrs={'type': 'date', 'min': datetime.today().strftime("%Y-%m-%d")}))
    time = forms.TimeField(label="Hora", widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = Appointment
        fields = ['attended_by', 'patient_id']
        labels = {
            'attended_by': _('Doctor'),
            'patient_id': _('Paciente'),
        }
    field_order = ['date', 'time', 'attended_by', 'patient_id']

    def clean(self):
        super(RegisterAppointmentForm, self).clean()
        date = self.cleaned_data['date']
        time = self.cleaned_data['time']
        doctor = self.cleaned_data['attended_by']
        if date and time:
            my_date_time = (date + ' ' + time + ':00')
            my_date_time = datetime.strptime(my_date_time, '%m/%d/%Y %H:%M:%S')
            collapsed_appointment = Appointment.objects.filter(attended_by=doctor, start_time__range=(my_date_time, my_date_time + timedelta(hours=1)))            
            if collapsed_appointment:
                msg = u"Existe una hora"
                self.add_error('time', '')
            if datetime.now() <= my_date_time:
                msg = u"¡Fecha inválida!"
                self.add_error('date', msg)
        return self.cleaned_data
