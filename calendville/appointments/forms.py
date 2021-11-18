from django import forms

class Register_appointment_form(forms.Form):
    inputDate = forms.DateField()
    inputTime = forms.TimeField()
    inputLastName = forms.CharField(max_length=100)
    inputName = forms.CharField(max_length=100)
    inputPatientID = forms.CharField(max_length=100)
    workerSelected = forms.CharField(max_length=100)
    inputEmail = forms.EmailField(max_length=100)


