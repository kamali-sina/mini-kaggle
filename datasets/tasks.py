"""
Create a tasks.py file per app to write its related tasks.

Example usage:
├── datasets
│   ├── tasks.py
│   ├── models.py
│   ├── views.py
│   ├── ...

in datasets/tasks.py:
    _____________________________________________________________________________________
    | from celery import shared_task                                                    |
    | from .models import Dataset                                                       |
    |                                                                                   |
    | @shared_task                                                                      |
    | def create_csv_dataset_with_string(input_string):                                 |
    |   ...                                                                             |
    _____________________________________________________________________________________

in datasets/views.py:
    _____________________________________________________________________________________
    | from datasets.tasks import create_random_user_accounts                            |
    |                                                                                   |
    | def create_dataset_view(request):                                                 |
    |   ...                                                                             |
    |   if form.is_valid():                                                             |
    |       create_csv_dataset_with_string.delay(form.cleaned_data['string_input']      |
    _____________________________________________________________________________________

!! don't use relative import for tasks. Also keep consistent import style: [app_name_as_in_INSTALLED_APPS_setting].tasks
"""
