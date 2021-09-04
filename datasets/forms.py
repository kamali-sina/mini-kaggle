import datetime
import re

from django import forms
from django.core.validators import RegexValidator

from datasets.services.tag_addition import get_unique_tags_validator_for_dataset, add_new_or_existing_tag, \
    TAG_INPUT_REGEX, TAG_INPUT_FORMAT_MESSAGE

from .models import Dataset


class CreateDatasetForm(forms.ModelForm):
    adding_tags = forms.CharField(label='Add as many space separated tags as you want',
                                  required=False,
                                  max_length=300,
                                  validators=[RegexValidator(regex=TAG_INPUT_REGEX, message=TAG_INPUT_FORMAT_MESSAGE)])

    class Meta:
        fields = ["title", "file", "description", 'is_public']
        model = Dataset
        widgets = {
            "description": forms.Textarea(),
        }

    def clean_adding_tags(self):
        return [] if not self.cleaned_data['adding_tags'] else set(re.split(r'\s+', self.cleaned_data['adding_tags']))

    def save(self, creator, commit=True, pk=0):
        dataset = super().save(commit=False)
        dataset.creator = creator
        if pk:
            dataset.id = pk
            dataset.date_created = datetime.datetime.now()
        if commit:
            dataset.save()
            self.save_tags(dataset)
        return dataset

    def save_tags(self, dataset):
        for tag_text in self.cleaned_data['adding_tags']:
            add_new_or_existing_tag(tag_text, dataset)


class EditDatasetInfoForm(forms.ModelForm):
    class Meta:
        model = Dataset
        fields = ['title', 'description']


class DeleteTagForm(forms.Form):
    deleting_tags = forms.ModelMultipleChoiceField(queryset=None,
                                                   required=False,
                                                   label='Select tags to delete')

    def __init__(self, *args, **kwargs):
        self.dataset = kwargs.pop('dataset')
        super().__init__(*args, **kwargs)
        dataset = Dataset.objects.get(id=self.dataset.id)
        self.fields['deleting_tags'].queryset = dataset.tags

    def submit(self):
        self.dataset.tags.remove(*self.cleaned_data['deleting_tags'])


class AddTagForm(forms.Form):
    adding_tags = forms.CharField(label='Add as many space separated tags as you want',
                                  required=False,
                                  max_length=300,
                                  validators=[
                                      RegexValidator(regex=TAG_INPUT_REGEX, message=TAG_INPUT_FORMAT_MESSAGE)])

    def __init__(self, *args, **kwargs):
        self.dataset = kwargs.pop('dataset')
        super().__init__(*args, **kwargs)
        self.fields['adding_tags'].validators.append(get_unique_tags_validator_for_dataset(self.dataset))

    def clean_adding_tags(self):
        return [] if not self.cleaned_data['adding_tags'] else set(re.split(r'\s+', self.cleaned_data['adding_tags']))

    def submit(self):
        for tag_text in self.cleaned_data['adding_tags']:
            add_new_or_existing_tag(tag_text, self.dataset)
