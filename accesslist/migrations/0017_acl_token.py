# Generated by Django 3.1.6 on 2021-06-30 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accesslist', '0016_auto_20210622_1919'),
    ]

    operations = [
        migrations.AddField(
            model_name='acl',
            name='token',
            field=models.CharField(blank=True, default='', max_length=64),
        ),
    ]