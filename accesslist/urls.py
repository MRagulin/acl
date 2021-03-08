from django.urls import path
from django.conf.urls import url
from .views import *

urlpatterns = [
    path("overview/", AclOver.as_view(), name="acloverview_urls"),
    path("overview/<uuid:acl_id>/", AclOver.as_view(), name="acloverview_urls"),

    path("test/", AclTest.as_view(), name="acltest_urls"),
    path("welcome/", AclDemo.as_view(), name="acldemo_urls"),

    path("info/<uuid:acl_id>/", AclCreate.as_view(), name="aclcreate_urls"),
    path("internal/<uuid:acl_id>/", AclCreate_internal.as_view(), name="aclinternal_urls"),
    path("external/<uuid:acl_id>/", AclCreate_external.as_view(), name="aclexternal_urls"),
    path("dmz/<uuid:acl_id>/", AclCreate_dmz.as_view(), name="acldmz_urls"),
    path("traffic/<uuid:acl_id>/", AclCreate_traffic.as_view(), name="acltraffic_urls"),


    path("info/", AclCreate.as_view(), name="aclcreate_urls"),
    path("internal/", AclCreate_internal.as_view(), name="aclinternal_urls"),
    path("external/", AclCreate_external.as_view(), name="aclexternal_urls"),
    path("traffic/", AclCreate_traffic.as_view(), name="acltraffic_urls"),
    path("dmz/", AclCreate_dmz.as_view(), name="acldmz_urls"),
    path("history/", Aclhistory.as_view(), name="aclhistory_urls"),

    path("checkip/<str:ip>/", CheckIp, name='check_ip_urls'),
    #url(r"^create/(?P<acl_id>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/$", AclCreate.as_view(), name="aclcreate_uuid_urls"),
    #url(r"^internal/(?P<acl_id>)/$", AclCreate_internal.as_view(), name="aclinternal_urls"),
    url("$^", ACldefault, name="acldefault_urls")
]

