from datasets.forms import EditDatasetInfoForm, DeleteTagForm, AddTagForm


def create_dataset_edition_forms_on_get(context, dataset):
    context['dataset_info_edition_form'] = EditDatasetInfoForm(instance=dataset)
    context['tag_deletion_form'] = DeleteTagForm(dataset=dataset)
    context['tag_addition_form'] = AddTagForm(dataset=dataset)


def create_dataset_edition_forms_on_post(context, form_data, dataset):
    context['dataset_info_edition_form'] = EditDatasetInfoForm(form_data, instance=dataset)
    context['tag_deletion_form'] = DeleteTagForm(form_data, dataset=dataset)
    context['tag_addition_form'] = AddTagForm(form_data, dataset=dataset)


def submit_dataset_edition_forms(context):
    context['dataset_info_edition_form'].save()
    context['tag_deletion_form'].submit()
    context['tag_addition_form'].submit()


def edition_forms_valid(context):
    return context['dataset_info_edition_form'].is_valid() and context['tag_deletion_form'].is_valid() and context[
        'tag_addition_form'].is_valid()
