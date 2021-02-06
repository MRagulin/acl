from django.db import models
from .utils import IP2Int

class Tags(models.Model):
    name = models.CharField(blank=True, max_length=64, unique=True)


class Vlans(models.Model):
    name = models.CharField(blank=True, max_length=64)
    location = models.CharField(blank=True, max_length=64)
    subnet = models.CharField(blank=True, max_length=15)
    vlan = models.IntegerField(default=0)
    mask = models.IntegerField(default=24)
    tags = models.ManyToManyField(Tags, null=True, blank=True, verbose_name='tags')

class Owners(models.Model):
    username = models.CharField(blank=True, max_length=64)

# class IpTags(models.Model):
#     tagname = models.CharField(blank=True, max_length=64, unique=True)

# IP address store.
class Iplist(models.Model):
    ipv4 = models.GenericIPAddressField(protocol='IPv4', unique=True)
    ipv4_int = models.BigIntegerField(default=0, db_index=True)
    hostname = models.CharField(blank=True, max_length=64)
    owner = models.ForeignKey(Owners, on_delete=models.CASCADE)
    comment = models.CharField(blank=True, max_length=256)
    tags = models.ManyToManyField('Tags', null=True, blank=True, verbose_name='tags') #on_delete=models.SET(0)
    vlan = models.ManyToManyField('Vlans', null=True, blank=True, verbose_name='vlans')

    def __str__(self):
        return "{}".format(self.ipv4)

    def save(self, *args, **kwargs):
        if self.ipv4 != '':
            try:
                self.ipv4_int = IP2Int(self.ipv4) or 0
            except:
                pass
        super().save(*args, **kwargs)

