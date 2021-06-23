from django.db import models
from ownerlist.models import Owners
from django.contrib.auth.models import User, Group

class ACL(models.Model):
    pkid = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(db_index=True, editable=False, unique=True)
    acltext = models.JSONField(blank=True, null=True, default=list)
    is_executed = models.BooleanField(null=True, default=False)
    owner = models.ForeignKey(User, null=True, on_delete=models.SET_NULL) #default=Owners.get_default_owner
    approve = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='approve_persone')
    taskid = models.CharField(blank=True, default="", editable=True, max_length=64)
    project = models.CharField(blank=True, max_length=128)
    created = models.DateField(blank=True, auto_now_add=True)
    APL_STATUS = [
        ('NOTFL', 'Не заполнено'),
        ('FL', 'Заполнено'),
        ('CMP', 'Выполнено'),
        ('WTE', 'Ожидает согласования'),
        ('APRV', 'Согласованно'),
        ('CNL', 'Отклонено')
    ]
    status = models.CharField(choices=APL_STATUS, default='NOTFL', blank=True, max_length=20)

