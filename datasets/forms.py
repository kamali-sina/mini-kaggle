import re

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.forms import inlineformset_factory

from datasets.services.conform_dataset import conform_dataset
from datasets.services.tags import save_tags

from .models import Dataset, DataSource, Column

TAG_INPUT_REGEX = r'^(?:[\w_0-9\.-]+)(?:\s*[\w_0-9\.-]+\s*)*$'
TAG_INPUT_FORMAT_MESSAGE = 'Tags should be space separated. Only letters, _ - and . are allowed.'


class CreateDatasetForm(forms.ModelForm):
    adding_tags = forms.CharField(label='Add tags',
                                  required=False,
                                  max_length=300,
                                  validators=[RegexValidator(regex=TAG_INPUT_REGEX, message=TAG_INPUT_FORMAT_MESSAGE)],
                                  widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self.creator = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        setattr(self.fields['adding_tags'], 'interactive_input', True)
        self.fields['data_source'].queryset = DataSource.objects.filter(creator=self.creator)

    class Meta:
        fields = ["title", "file", "description", 'is_public', 'data_source']
        model = Dataset
        widgets = {
            "description": forms.Textarea(),
        }

    def clean_adding_tags(self):
        return [] if not self.cleaned_data['adding_tags'] else set(re.split(r'\s+', self.cleaned_data['adding_tags']))

    def clean(self):
        cleaned_data = super().clean()
        dataset_title = cleaned_data['title']
        is_public = cleaned_data['is_public']
        data_source = cleaned_data['data_source']
        file = cleaned_data['file']
        if Dataset.objects.filter(is_public=is_public).filter(title=dataset_title):
            raise ValidationError('Dataset name already used!')
        try:
            conform_dataset(file, data_source)
        except Exception as exc:
            raise ValidationError(exc) from exc

    def save(self, commit=True):
        dataset = super().save(commit=False)
        dataset.creator = self.creator
        if commit:
            dataset.save()
            save_tags(self.cleaned_data['adding_tags'], dataset)
        return dataset


class UpdateDatasetForm(forms.ModelForm):
    adding_tags = forms.CharField(label='Add tags',
                                  required=False,
                                  max_length=300,
                                  validators=[
                                      RegexValidator(regex=TAG_INPUT_REGEX, message=TAG_INPUT_FORMAT_MESSAGE)],
                                  widget=forms.HiddenInput())
    deleting_tags = forms.ModelMultipleChoiceField(queryset=None,
                                                   required=False,
                                                   label='Select tags to delete',
                                                   widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        setattr(self.fields['adding_tags'], 'interactive_input', True)
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


class CreateDataSourceForm(forms.ModelForm):
    class Meta:
        fields = ["title", "description"]
        model = DataSource
        widgets = {
            "description": forms.Textarea(),
        }

    def save(self, creator, commit=True):
        datasource = super().save(commit=False)
        datasource.creator = creator
        datasource.save()
        return datasource

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data['title']
        if DataSource.objects.filter(title=title):
            raise ValidationError('Data source name already used!')


TYPE_CHOICES = [
    ("int", "Integer"),
    ("object", "String"),
    ("bool", "Boolean"),
    ("float", "Floating point"),
    ("double", "Double"),
]


class ColumnForm(forms.ModelForm):
    type = forms.CharField(label='Column type', widget=forms.Select(choices=TYPE_CHOICES))

    class Meta:
        fields = ['title', 'type']
        model = Column

    def save(self, commit=True):
        column = super().save(commit=False)
        column.save()
        return column


ColumnsFormSet = inlineformset_factory(DataSource, Column, form=ColumnForm, extra=1, can_delete=False)
