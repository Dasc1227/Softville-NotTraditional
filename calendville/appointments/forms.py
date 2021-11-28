from datetime import datetime, timedelta
from django import forms
from django.utils.translation import gettext_lazy as _

from appointments.models import Appointment


class RegisterAppointmentForm(forms.ModelForm):
    date = forms.DateField(label="Fecha",
                           required=True,
                           widget=forms.DateInput(
                               attrs={
                                   'type': 'date',
                                   'min': datetime.today().strftime("%Y-%m-%d")
                               }
                           ))
    time = forms.TimeField(label="Hora",
                           required=True,
                           widget=forms.TimeInput(attrs={'type': 'time'}))

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
            appointment_datetime = datetime.combine(date, time)
            prev_appointment = appointment_datetime - timedelta(minutes=59)
            collapsed_appointment = Appointment.objects.filter(
                attended_by=doctor,
                start_time__range=(prev_appointment,
                                   appointment_datetime)
            )
            if collapsed_appointment:
                msg = "El doctor ya tiene una cita en ese momento."
                self.add_error('time', msg)
            if appointment_datetime <= datetime.now():
                msg = "¡Fecha inválida!"
                self.add_error('date', msg)
        return self.cleaned_data
