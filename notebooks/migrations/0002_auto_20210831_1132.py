# Generated by Django 3.2.6 on 2021-08-31 07:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('notebooks', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cell',
            name='result',
        ),
        migrations.AddField(
            model_name='cell',
            name='notebook',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='notebooks.notebook'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cell',
            name='cell_status',
            field=models.CharField(choices=[('R', 'Running'), ('D', 'Done'), ('N', 'None')], default='N', max_length=1),
        ),
    ]
