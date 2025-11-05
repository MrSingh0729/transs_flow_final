from django import forms
from .models import Employee

class EmployeeForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)  # optional for edit

    class Meta:
        model = Employee
        fields = [
            'employee_id', 'full_name', 'role', 'department',
            'factory_code', 'factory_name', 'country_code', 'country_name', 'password'
        ]
