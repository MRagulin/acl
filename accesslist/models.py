from django.db import models
from ownerlist.models import Owners


class ACL(models.Model):
    pkid = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(db_index=True, editable=False, unique=True)
    acltext = models.JSONField(blank=True, null=True, default=list)
    is_executed = models.BooleanField(null=True, default=False)
    owner = models.ForeignKey(Owners, null=True, on_delete=models.SET_NULL, default=Owners.get_default_owner)
    project = models.CharField(blank=True, max_length=128)
    created = models.DateField(blank=True, auto_now_add=True)
    APL_STATUS = [
        ('NOTFL', 'Не заполнено'),
        ('FL', 'Заполнено'),
        ('CMP', 'Выполнено'),
        ('WTE', 'Ожидает рассмотрения'),
        ('CNL', 'Отклонено')
    ]
    status = models.CharField(choices=APL_STATUS, default='NOTFL', blank=True, max_length=20)
