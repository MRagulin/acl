# Generated by Django 3.1.6 on 2021-04-14 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accesslist', '0011_acl_project'),
    ]

    operations = [
        migrations.AddField(
            model_name='acl',
            name='taskid',
            field=models.CharField(default='0', max_length=64),
        ),
    ]
