from django.urls import path
from django.conf.urls import url
from .views import SearchView, TreeView

urlpatterns = [
    path('ipconfig/', SearchView.as_view(), name="ipconfig_urls"),
    url('search/', SearchView.as_view(), name="search"),
    url(r'^$', TreeView.as_view(), name="ipconfig_urls"),
]
