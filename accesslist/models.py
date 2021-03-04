from django.db import models
from ownerlist.models import Owners
from datetime import date


class ACL(models.Model):
    pkid = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(db_index=True, editable=False, unique=True)
    acltext = models.JSONField(blank=True)
    is_executed = models.BooleanField(null=True, default=False)
    owner = models.CharField(max_length=64, blank=True, default='admin')
    created = models.DateField(blank=True, auto_now_add=True)