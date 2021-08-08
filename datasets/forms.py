from django import forms
from .models import Dataset
from django.core.validators import FileExtensionValidator


class CreateDatasetForm(forms.ModelForm):
    file = forms.FileField(
        label="Filepath:",
        help_text="Only csv files",
        widget=forms.FileInput(),
        validators=[
            FileExtensionValidator(allowed_extensions=["csv"]),
        ],
    )

    class Meta:
        fields = ["file", "title", "description"]
        model = Dataset
