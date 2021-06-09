from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from .views import *

urlpatterns = [
    path('', PanelView.as_view(), name="panel_adm"),
]