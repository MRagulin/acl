from django.db import models
from .utils import IP2Int


class Tags(models.Model):
    name = models.CharField(max_length=128, unique=True, verbose_name="Имя тега", default="default")

    def save(self, *args, **kwargs):
        if str(self.name).strip() == '':
            self.name = 'DEFAULT'
        super().save(*args, **kwargs)

    def __str__(self):
        return "Тег: {}".format(self.name)

class Vlans(models.Model):
    name = models.CharField(blank=True, max_length=64, verbose_name="Имя VLAN")
    location = models.CharField(blank=True, max_length=64)
    subnet = models.CharField(blank=True, max_length=15)
    vlan = models.IntegerField(default=0)
    mask = models.IntegerField(default=24)
    tags = models.ManyToManyField(Tags, null=True, blank=True, verbose_name='tags')

    def __str__(self):
        return "VLAN: {}".format(self.name)

class Owners(models.Model):
    username = models.CharField(blank=True, max_length=256, verbose_name="Имя владельца")
    #account = models.CharField(blank=True, max_length=256, verbose_name="Аккаунт")
    email = models.EmailField(blank=True)
    phone = models.CharField(blank=True, max_length=256, verbose_name="Телефон")
    active = models.BooleanField(null=True, default=True)
    department = models.CharField(blank=True, max_length=256, verbose_name="Департамент")

    @classmethod
    def get_default_owner(cls):
        owner, obj = Owners.objects.get_or_create(username='Unknown')
        return owner.pk

    def __str__(self):
        return "Владелец: {}".format(self.username)

class Iplist(models.Model):
    ipv4 = models.GenericIPAddressField(protocol='IPv4', unique=True, verbose_name="IP адресс", db_index=True)
    ipv4_int = models.BigIntegerField(default=0, db_index=True)
    ipv4_str = models.CharField(blank=True, max_length=15)
    hostname = models.CharField(blank=True, max_length=64)
    owner = models.ForeignKey(Owners, null=True, on_delete=models.SET_NULL, default=Owners.get_default_owner)
    comment = models.TextField(blank=True, null=True)
    tags = models.ManyToManyField('Tags', null=True, blank=True, verbose_name='tags')
    vlan = models.ManyToManyField('Vlans', null=True, blank=True, verbose_name='vlans')

    def __str__(self):
        return "IP адрес: {}".format(self.ipv4)

    """Переопределяем IP как Int значения"""
    def save(self, *args, **kwargs):
        if self.ipv4 != '':
            try:
                self.ipv4_int = IP2Int(self.ipv4) or 0
            except:
                pass

            try:
                self.ipv4_str = ".".join(self.ipv4.split('.')[:3])
            except:
                pass

        super().save(*args, **kwargs)


class HistoryCall(models.Model):
    string = models.TextField(blank=True)
    status = models.BooleanField(default=False, verbose_name="Is result")
    ipv4 = models.ForeignKey(Iplist, null=True, on_delete=models.SET_NULL)
    username = models.CharField(blank=True, max_length=64)
    date = models.DateTimeField(auto_now_add=True, blank=True)

