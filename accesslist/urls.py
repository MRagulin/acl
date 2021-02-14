from django.urls import path
from django.conf.urls import url
from .views import AclView

urlpatterns = [
    path("create/", AclView.as_view(), name="aclcreate_urls"),
    path("update/", AclView.as_view(), name="aclview_urls"),

]
