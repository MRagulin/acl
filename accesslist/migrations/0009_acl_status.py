# Generated by Django 3.1.6 on 2021-03-06 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accesslist', '0008_auto_20210305_1259'),
    ]

    operations = [
        migrations.AddField(
            model_name='acl',
            name='status',
            field=models.CharField(blank=True, choices=[('NOTFL', 'Не заполнено'), ('FL', 'Заполнено'), ('CMP', 'Выполнено'), ('WTE', 'Ожидает рассмотрения'), ('CNL', 'Отклонено')], default='NOTFL', max_length=20),
        ),
    ]