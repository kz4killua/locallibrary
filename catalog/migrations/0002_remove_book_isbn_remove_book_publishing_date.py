# Generated by Django 4.0.4 on 2022-07-05 21:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='isbn',
        ),
        migrations.RemoveField(
            model_name='book',
            name='publishing_date',
        ),
    ]
