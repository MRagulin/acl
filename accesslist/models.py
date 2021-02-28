from django.db import models
from django.contrib.postgres.fields import JSONField
from ownerlist.models import Owners
import uuid


class ACL(models.Model):
    pkid = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(primary_key=True, editable=False)
    acltext = JSONField()
    is_executed = models.BooleanField(null=True, default=False)

    class Meta:
        abstract = True
