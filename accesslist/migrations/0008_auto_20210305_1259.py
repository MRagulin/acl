# Generated by Django 3.1.6 on 2021-03-05 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accesslist', '0007_auto_20210303_2334'),
    ]

    operations = [
        migrations.AlterField(
            model_name='acl',
            name='acltext',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
    ]
