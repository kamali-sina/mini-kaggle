import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from datasets.models import Tag

TAG_INPUT_REGEX = r'^(?:[\w_0-9\.-]+)(?:\s*[\w_0-9\.-]+\s*)*$'
TAG_INPUT_FORMAT_MESSAGE = 'Tags should be space separated. Only letters, _ - and . are allowed.'


def add_new_or_existing_tag(tag_text, dataset):
    try:
        tag = dataset.creator.tags.get(text=tag_text)
        dataset.tags.add(tag)
    except Tag.DoesNotExist:
        tag = Tag.objects.create(creator=dataset.creator, text=tag_text)
        dataset.tags.add(tag)


def get_unique_tags_validator_for_dataset(dataset):
    def validator(value):
        duplicate_tags = dataset.tags.filter(text__in=re.split(r'\s+', value))
        if duplicate_tags:
            raise ValidationError(
                _('The tag %(value)s already exists in this dataset'),
                params={'value': duplicate_tags[0]},
            )

    return validator
