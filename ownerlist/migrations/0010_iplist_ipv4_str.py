# Generated by Django 3.1.6 on 2021-02-11 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ownerlist', '0009_auto_20210210_2208'),
    ]

    operations = [
        migrations.AddField(
            model_name='iplist',
            name='ipv4_str',
            field=models.CharField(blank=True, max_length=15),
        ),
    ]
