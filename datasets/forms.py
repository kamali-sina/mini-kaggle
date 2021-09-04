import re

from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

from datasets.services.tags import save_tags

from .models import Dataset

TAG_INPUT_REGEX = r'^(?:[\w_0-9\.-]+)(?:\s*[\w_0-9\.-]+\s*)*$'
TAG_INPUT_FORMAT_MESSAGE = 'Tags should be space separated. Only letters, _ - and . are allowed.'


class CreateDatasetForm(forms.ModelForm):
    adding_tags = forms.CharField(label='Add as many space separated tags as you want',
                                  required=False,
                                  max_length=300,
                                  validators=[RegexValidator(regex=TAG_INPUT_REGEX, message=TAG_INPUT_FORMAT_MESSAGE)])

    def __init__(self, *args, **kwargs):
        self.creator = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    class Meta:
        fields = ["title", "file", "description", 'is_public']
        model = Dataset
        widgets = {
            "description": forms.Textarea(),
        }

    def clean_adding_tags(self):
        return [] if not self.cleaned_data['adding_tags'] else set(re.split(r'\s+', self.cleaned_data['adding_tags']))

    def save(self, commit=True):
        dataset = super().save(commit=False)
        dataset.creator = self.creator
        if commit:
            dataset.save()
            save_tags(self.cleaned_data['adding_tags'], dataset)
        return dataset


class UpdateDatasetForm(forms.ModelForm):
    adding_tags = forms.CharField(label='Add as many space separated tags as you want',
                                  required=False,
                                  max_length=300,
                                  validators=[
                                      RegexValidator(regex=TAG_INPUT_REGEX, message=TAG_INPUT_FORMAT_MESSAGE)])
    deleting_tags = forms.ModelMultipleChoiceField(queryset=None,
                                                   required=False,
                                                   label='Select tags to delete',
                                                   widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['deleting_tags'].queryset = self.instance.tags

    class Meta:
        model = Dataset
        fields = ['title', 'description']

    def clean_adding_tags(self):
        return [] if not self.cleaned_data['adding_tags'] else set(re.split(r'\s+', self.cleaned_data['adding_tags']))

    def clean(self):
        cleaned_data = super().clean()
        duplicate_tag = self.instance.tags.filter(text__in=cleaned_data.get('adding_tags', '')).first()
        if duplicate_tag:
            raise ValidationError(f'The tag {duplicate_tag} already exists in this dataset')

    def save(self, commit=True):
        dataset = super().save()
        if commit:
            dataset.save()
            dataset.tags.remove(*self.cleaned_data['deleting_tags'])
            save_tags(self.cleaned_data['adding_tags'], dataset)
        return dataset
