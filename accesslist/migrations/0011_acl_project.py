# Generated by Django 3.1.6 on 2021-03-09 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accesslist', '0010_auto_20210309_1411'),
    ]

    operations = [
        migrations.AddField(
            model_name='acl',
            name='project',
            field=models.CharField(blank=True, max_length=128),
        ),
    ]
