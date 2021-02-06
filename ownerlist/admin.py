from django.contrib import admin
from .models import Iplist, Tags, Vlans, Owners
# Register your models here.
admin.site.register(Iplist)
admin.site.register(Tags)
admin.site.register(Vlans)
admin.site.register(Owners)
