from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Iplist)
admin.site.register(Owners)
admin.site.register(Vlans)
admin.site.register(Tags)

