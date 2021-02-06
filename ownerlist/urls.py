from django.urls import path
from django.conf.urls import url
from .views import SearchView

urlpatterns = [
    path("ipconfig/", SearchView.as_view(), name="ipconfig_urls"),
    url(r'^$', SearchView.as_view(), name="ipconfig_urls"), #test, delete prod
]
