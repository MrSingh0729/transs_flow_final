from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.core.files.images import get_image_dimensions

from .models import Employee, PasswordChangeRequest


# ========================= LOGIN FORM =========================

class EmployeeLoginForm(forms.Form):

    employee_id = forms.CharField(
        label="Employee ID",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your employee ID",
            "autocomplete": "username"
        })
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your password",
            "autocomplete": "current-password"
        })
    )

    remember_me = forms.BooleanField(
        required=False,
        label="Remember Me",
        widget=forms.CheckboxInput(attrs={
            "class": "form-check-input"
        })
    )


# ========================= PROFILE UPDATE FORM =========================

class EmployeeProfileForm(forms.ModelForm):

    class Meta:
        model = Employee
        fields = [
            'full_name',
            'email',
            'phone_number',
            'role',
            'department',
            'factory_code',
            'factory_name',
            'country_code',
            'country_name',
            'profile_picture'
        ]

        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'factory_code': forms.TextInput(attrs={'class': 'form-control'}),
            'factory_name': forms.TextInput(attrs={'class': 'form-control'}),
            'country_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country_name': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control'})
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Employee.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This email is already registered.")
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone and not phone.isdigit():
            raise ValidationError("Phone number should contain only digits.")
        return phone

    def clean_profile_picture(self):
        picture = self.cleaned_data.get('profile_picture')

        if picture:
            try:
                width, height = get_image_dimensions(picture)
            except Exception:
                raise ValidationError("Invalid image file.")

            if picture.size > 5 * 1024 * 1024:
                raise ValidationError("Image size must be under 5MB.")

            if width < 200 or height < 200:
                raise ValidationError("Image must be at least 200x200 px.")

            valid_formats = ['jpg', 'jpeg', 'png', 'webp']
            ext = picture.name.split('.')[-1].lower()

            if ext not in valid_formats:
                raise ValidationError("Only JPG, PNG or WEBP images are allowed.")

        return picture


# ========================= PASSWORD CHANGE REQUEST FORM =========================

class PasswordChangeRequestForm(forms.ModelForm):

    class Meta:
        model = PasswordChangeRequest
        fields = ['request_reason']
        widgets = {
            'request_reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Explain why you want to change password'
            })
        }


# ========================= CREATE EMPLOYEE FORM =========================

class EmployeeCreateForm(forms.ModelForm):

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        validators=[validate_password]
    )

    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = Employee
        fields = [
            'employee_id',
            'full_name',
            'email',
            'role',
            'department',
            'factory_code',
            'factory_name',
            'country_code',
            'country_name'
        ]

        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'factory_code': forms.TextInput(attrs={'class': 'form-control'}),
            'factory_name': forms.TextInput(attrs={'class': 'form-control'}),
            'country_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country_name': forms.TextInput(attrs={'class': 'form-control'})
        }

    def clean_employee_id(self):
        emp_id = self.cleaned_data.get('employee_id')
        if Employee.objects.filter(employee_id__iexact=emp_id).exists():
            raise ValidationError("Employee ID already exists.")
        return emp_id

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Employee.objects.filter(email__iexact=email).exists():
            raise ValidationError("Email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")

        if password and confirm and password != confirm:
            raise ValidationError("Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()

        return user


# ========================= ADMIN PASSWORD RESET FORM =========================

class AdminPasswordResetForm(forms.Form):

    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        validators=[validate_password]
    )

    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            raise ValidationError("Passwords do not match.")

        return cleaned_data


# ========================= ADMIN REQUEST ACTION FORM =========================

class PasswordChangeActionForm(forms.Form):

    action = forms.ChoiceField(
        choices=[('approve', 'Approve'), ('reject', 'Reject')],
        widget=forms.RadioSelect
    )

    admin_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 3,
            "placeholder": "Optional admin notes..."
        })
    )
