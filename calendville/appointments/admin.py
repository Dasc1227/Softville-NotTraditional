from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from importlib_resources._common import _

from appointments.models import Appointment
from appointments.models import Patient


class WorkerAdmin(UserAdmin):
    """Define admin model for custom User model with no username field."""
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {
            'fields':
                (
                    'id_number', 'id_type', 'first_name', 'last_name'
                )}),
        (_('Permissions'), {
            'fields':
                (
                    'is_active', 'is_staff', 'is_superuser',
                    'password_attempts', 'groups',
                    'user_permissions'
                )}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'id_number'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)


admin.site.register(get_user_model(), WorkerAdmin)
admin.site.register(Appointment)
admin.site.register(Patient)
