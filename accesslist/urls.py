from django.urls import path
from django.conf.urls import url
from .views import AclCreate, AclOver, AclCreate_internal, AclCreate_dmz, AclTest, AclCreate_external, AclCreate_traffic, AclDemo

urlpatterns = [
    path("overview/", AclOver.as_view(), name="acloverview_urls"),
    path("internal/", AclCreate_internal.as_view(), name="aclinternal_urls"),
    path("external/", AclCreate_external.as_view(), name="aclexternal_urls"),
    path("traffic/", AclCreate_traffic.as_view(), name="acltraffic_urls"),
    path("dmz/", AclCreate_dmz.as_view(), name="acldmz_urls"),
    path("create/", AclCreate.as_view(), name="aclcreate_urls"),
    path("test/", AclTest.as_view(), name="acltest_urls"),
    path("demo/", AclDemo.as_view(), name="acldemo_urls"),
]

