# Generated by Django 3.1 on 2021-04-07 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ownerlist', '0014_owners_department'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tags',
            name='name',
            field=models.CharField(default='default', max_length=128, unique=True, verbose_name='Имя тега'),
        ),
    ]
