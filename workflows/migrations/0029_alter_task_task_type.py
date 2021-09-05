# Generated by Django 3.2.6 on 2021-09-02 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflows', '0028_merge_20210831_1208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='task_type',
            field=models.CharField(choices=[('DC', 'Docker'), ('PY', 'Python')], default='DC', max_length=2),
        ),
    ]
