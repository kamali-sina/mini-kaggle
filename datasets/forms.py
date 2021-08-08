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

    description = forms.CharField(
         max_length=200,
         required=False,
    )

    is_public = forms.BooleanField(
        required=False
    )

    class Meta:
        fields = ["description", "file", "is_public"]
        model = Dataset
