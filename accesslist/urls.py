from django.urls import path, re_path, include
from django.conf.urls import url
from .views import *

urlpatterns = [
    path("overview/", AclOver.as_view(), name="acloverview_urls"),


    path("test/", AclTest.as_view(), name="acltest_urls"),
    path("welcome/", AclDemo.as_view(), name="acldemo_urls"),
    path("history/", Aclhistory.as_view(), name="aclhistory_urls"),

  #  path("info/<uuid:acl_id>/new/", AclCreate.as_view(), name="aclcreate_urls"),
    #path("internal/<uuid:acl_id>/new/", AclCreate_internal.as_view(), name="aclinternal_urls"),
    #path("external/<uuid:acl_id>/new/", AclCreate_external.as_view(), name="aclexternal_urls"),
    #path("dmz/<uuid:acl_id>/new/", AclCreate_dmz.as_view(), name="acldmz_urls"),
    #path("traffic/<uuid:acl_id>/new/", AclCreate_traffic.as_view(), name="acltraffic_urls"),
    #path("history/<uuid:acl_id>/", Aclhistory.as_view(), name="aclhistory_uuid_urls"),


    # path("info/<uuid:acl_id>/edit/", AclCreateEdit.as_view(), name="aclcreate_editurls"),
    # path("internal/<uuid:acl_id>/edit/", AclCreate_internalEdit.as_view(), name="aclinternal_edit_urls"),
    # path("external/<uuid:acl_id>/edit/", AclCreate_externalEdit.as_view(), name="aclexternal_edit_urls"),
    # path("dmz/<uuid:acl_id>/edit/", AclCreate_dmzEdit.as_view(), name="acldmz_edit_urls"),
    # path("traffic/<uuid:acl_id>/edit/", AclCreate_trafficEdit.as_view(), name="acltraffic_edit_urls"),

    re_path("info/", include([
        url(r"^$", AclCreate.as_view(), name="aclcreate_urls"),
        url(r"^(?P<acl_id>[0-9a-f-]+)/$", AclCreate.as_view(), name="aclcreate_urls"),
        url(r"^(?P<acl_id>[0-9a-f-]+)/new/$", AclCreate.as_view(), name="aclcreate_urls"),
    ])),
        # url(r'^$', )                                                  ))),#name="aclcreate_edit"
    # re_path("info/", AclCreate.as_view(), name="aclcreate_urls"), #|/$
    #path("internal/", AclCreate_internal.as_view(), name="aclinternal_urls"),
    re_path("internal/", include([
        url(r"^$", AclCreate.as_view(), name="aclinternal_urls"),
        url(r"^(?P<acl_id>[0-9a-f-]+)/$", AclCreate_internal.as_view(), name="aclinternal_urls"),
        url(r"^(?P<acl_id>[0-9a-f-]+)/new/$", AclCreate_internal.as_view(), name="aclinternal_urls"),
    ])),

    re_path("external/", include([
        url(r"^$", AclCreate_external.as_view(), name="aclexternal_urls"),
        url(r"^(?P<acl_id>[0-9a-f-]+)/$", AclCreate_external.as_view(), name="aclexternal_urls"),
        url(r"^(?P<acl_id>[0-9a-f-]+)/new/$", AclCreate_external.as_view(), name="aclexternal_urls"),
    ])),

    re_path("traffic/", include([
        url(r"^$", AclCreate_traffic.as_view(), name="acltraffic_urls"),
        url(r"^(?P<acl_id>[0-9a-f-]+)/$", AclCreate_traffic.as_view(), name="acltraffic_urls"),
        url(r"^(?P<acl_id>[0-9a-f-]+)/new/$", AclCreate_traffic.as_view(), name="acltraffic_urls"),
    ])),

    re_path("dmz/", include([
        url(r"^$", AclCreate_dmz.as_view(), name="acldmz_urls"),
        url(r"^(?P<acl_id>[0-9a-f-]+)/$", AclCreate_dmz.as_view(), name="acldmz_urls"),
        url(r"^(?P<acl_id>[0-9a-f-]+)/new/$", AclCreate_dmz.as_view(), name="acldmz_urls"),
    ])),

    re_path("overview/", include([
        url(r"^$", AclCreate_dmz.as_view(), name="acloverview_urls"),
        url(r"^(?P<acl_id>[0-9a-f-]+)/$", AclOver.as_view(), name="acloverview_urls"),
        url(r"^(?P<acl_id>[0-9a-f-]+)/new/$", AclOver.as_view(), name="acloverview_urls"),
    ])),
    #path("overview/<uuid:acl_id>/new/", AclOver.as_view(), name="acloverview_urls"),
    #path("external/", AclCreate_external.as_view(), name="aclexternal_urls"),
    #path("traffic/", AclCreate_traffic.as_view(), name="acltraffic_urls"),
    #path("dmz/", AclCreate_dmz.as_view(), name="acldmz_urls"),




    path("checkip/<str:ip>/", CheckIp, name='check_ip_urls'),
    path("remove/", AclRemove, name="acl_remove"),
    #url(r"^create/(?P<acl_id>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/$", AclCreate.as_view(), name="aclcreate_uuid_urls"),
    #url(r"^internal/(?P<acl_id>)/$", AclCreate_internal.as_view(), name="aclinternal_urls"),
    url("$^", ACldefault, name="acldefault_urls")
]

