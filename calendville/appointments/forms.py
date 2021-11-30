from datetime import datetime, timedelta
from django import forms
from django.utils.translation import gettext_lazy as _

from appointments.models import Appointment, HealthProcedure
from appointments.models import Patient


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
        if len(self.cleaned_data) == 4:
            date = self.cleaned_data['date']
            time = self.cleaned_data['time']
            doctor = self.cleaned_data['attended_by']
            patient = self.cleaned_data['patient_id']
            appointment_datetime = datetime.combine(date, time)
            prev_appointment = appointment_datetime - timedelta(minutes=59)
            future_appointment = appointment_datetime + timedelta(minutes=59)
            overlapped_doctor_appointment = Appointment.objects.filter(
                attended_by=doctor,
                start_time__range=(prev_appointment,
                                   future_appointment)
            )
            overlapped_patient_appointment = Appointment.objects.filter(
                patient_id=patient,
                start_time__range=(prev_appointment,
                                   future_appointment)
            )
            if overlapped_doctor_appointment:
                msg = u"El doctor ya tiene una cita en ese momento."
                self.add_error('attended_by', msg)
            if overlapped_patient_appointment:
                msg = u"El paciente ya tiene una cita en ese momento."
                self.add_error('patient_id', msg)
            if appointment_datetime.date() < datetime.today().date():
                msg = u"¡Fecha inválida!"
                self.add_error('date', msg)
            if appointment_datetime.date() == datetime.today().date() \
                    and appointment_datetime.time() < datetime.now().time():
                msg = u"¡Hora inválida!"
                self.add_error('time', msg)
        return self.cleaned_data


class RegisterHealthProcedureForm(forms.ModelForm):

    class Meta:
        model = HealthProcedure
        exclude = ['creation_date']
        labels = {
            'name': _('Nombre'),
            'assigned_to': _('Paciente'),
            'details': _('Detalles'),
        }
        widgets = {
            'details': forms.Textarea(attrs={'cols': 80, 'rows': 20})
        }


class RegisterPatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['id_number', 'name', 'last_name', 'email']
        labels = {
            'id_number': _('Cedula'),
            'name': _('Nombre'),
            'last_name': _('Apellidos'),
            'email': _('Correo'),
        }
        field_order = ['id_number', 'name', 'last_name', 'email']
