from datasets.models import Tag


def save_tags(tags, dataset):
    """Gets a list of tag names, creates tag objects for those not already existing for the creator of the dataset,
     and adds the tags to the dataset"""
    for tag_text in tags:
        if not dataset.creator.tags.filter(text=tag_text).exists():
            tag = Tag.objects.create(creator=dataset.creator, text=tag_text)
        else:
            tag = dataset.creator.tags.get(text=tag_text)
        dataset.tags.add(tag)
