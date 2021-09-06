# Generated by Django 3.2.6 on 2021-09-06 16:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0008_alter_dataset_data_source'),
        ('notebooks', '0005_auto_20210904_1329'),
    ]

    operations = [
        migrations.AddField(
            model_name='notebook',
            name='accessible_datasets',
            field=models.ManyToManyField(blank=True, to='datasets.Dataset'),
        ),
        migrations.AlterField(
            model_name='notebook',
            name='session',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notebook', to='notebooks.session'),
        ),
    ]
