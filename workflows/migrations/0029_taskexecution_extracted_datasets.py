# Generated by Django 3.2.5 on 2021-08-31 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0006_alter_dataset_tags'),
        ('workflows', '0028_merge_20210831_1208'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskexecution',
            name='extracted_datasets',
            field=models.ManyToManyField(blank=True, to='datasets.Dataset'),
        ),
    ]
