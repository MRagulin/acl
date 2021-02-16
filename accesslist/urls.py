from django.urls import path
from django.conf.urls import url
from .views import AclCreate, AclOver

urlpatterns = [
    path("overview/", AclOver.as_view(), name="acloverview_urls"),
    path("create/", AclCreate.as_view(), name="aclcreate_urls"),
]
