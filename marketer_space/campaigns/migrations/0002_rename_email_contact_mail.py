# Generated by Django 4.1 on 2022-09-29 15:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contact',
            old_name='email',
            new_name='mail',
        ),
    ]
