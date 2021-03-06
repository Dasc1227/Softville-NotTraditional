
import re
from datetime import datetime, timedelta, time
from django import forms
from django.utils.timezone import make_aware
from django.utils.translation import gettext_lazy as _

from appointments.models import (
    Appointment,
    HealthProcedure,
    Patient,
    Worker,
)


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
            appointment_date = self.cleaned_data['date']
            appointment_time = self.cleaned_data['time']
            doctor = self.cleaned_data['attended_by']
            patient = self.cleaned_data['patient_id']
            appointment_datetime = datetime.combine(appointment_date,
                                                    appointment_time)
            prev_appointment = make_aware(
                appointment_datetime - timedelta(minutes=59)
            )
            future_appointment = make_aware(
                appointment_datetime + timedelta(minutes=59)
            )
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
                msg = u"??Fecha inv??lida!"
                self.add_error('date', msg)
            if appointment_datetime.date() == datetime.today().date() \
                    and appointment_datetime.time() < datetime.now().time():
                msg = u"??Hora inv??lida!"
                self.add_error('time', msg)
            if time(11, 0, 0) > appointment_datetime.time() or \
                    appointment_datetime.time() > time(21, 0, 0):
                msg = u"Las horas de cita solo " \
                      u"pueden ser entre las 11:00 y 21:00."
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
            'details': forms.Textarea(attrs={'cols': 40, 'rows': 10})
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
        widgets = {
            'id_number': forms.TextInput(attrs={
                'pattern': r'[1-9]-?\d{4}-?\d{4}'
            })
        }
        field_order = ['id_number', 'name', 'last_name', 'email']

    def clean(self):
        super(RegisterPatientForm, self).clean()
        if len(self.cleaned_data) == 4:
            id_number = self.cleaned_data['id_number']
            ID_PATTERN = r'^[1-9]-?\d{4}-?\d{4}$'
            regex = re.compile(ID_PATTERN)
            if not regex.search(id_number):
                msg = u"La c??dula es inv??lida."
                self.add_error('id_number', msg)
        return self.cleaned_data


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Correo", max_length=254, required=True,
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "id": "email"
        })
    )
    password = forms.CharField(
        label="Contrase??a", required=True,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "id": "password"
        })
    )
    next = forms.CharField(
        widget=forms.HiddenInput(attrs={"id": "next"}),
        required=False
    )

    def clean(self):
        super(LoginForm, self).clean()
        if len(self.cleaned_data) < 2:
            return

        email = self.cleaned_data["email"]
        user_entry = Worker.objects.filter(email=email)
        if not user_entry.exists():
            error = u"El correo no existe en el sistema"
            self.add_error("email", error)

        next = self.cleaned_data["next"]
        if len(next) > 0 and not next.startswith("/"):
            error = u"No es posible redireccionar a sitios externos"
            self.add_error("next", error)
