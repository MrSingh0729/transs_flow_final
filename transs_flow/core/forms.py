from django import forms
from .models import IssueReport

class IssueReportForm(forms.ModelForm):
    class Meta:
        model = IssueReport
        fields = [
            'issue_name',
            'description',
            'severity',
            'line_leader',
            'operator_id'
        ]


class IssueImageUploadForm(forms.Form):
    images = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            "accept": "image/*",
            "capture": "camera"
        })
    )