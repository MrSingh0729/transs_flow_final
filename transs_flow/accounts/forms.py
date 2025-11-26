from django import forms
from .models import Employee, PasswordChangeRequest


class EmployeeForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)  # optional for edit

    class Meta:
        model = Employee
        fields = [
            'employee_id', 'full_name', 'role', 'department',
            'factory_code', 'factory_name', 'country_code', 'country_name', 'password'
        ]


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['full_name', 'email', 'contact_number', 'bio', 'profile_picture']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
        }


class ForgotPasswordRequestForm(forms.Form):
    employee_id = forms.CharField(max_length=20, label="Employee ID")


class AdminPasswordChangeForm(forms.Form):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput,
        label="New Password"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirm New Password"
    )

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("new_password1")
        p2 = cleaned.get("new_password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned
