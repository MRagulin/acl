from django.urls import path, re_path, include
from django.conf.urls import url
from .views import *

urlpatterns = [
    path("overview/", AclOver.as_view(), name="acloverview_urls"),
    path("welcome/", AclDemo.as_view(), name="acldemo_urls"),
    path("history/", Aclhistory.as_view(), name="aclhistory_urls"),
    path("history/<uuid:acl_id>/", Aclhistory.as_view(), name="aclhistory_urls"),

    re_path("info/", include([
        url(r"^$", AclCreate.as_view(), name="aclcreate_urls"),
        url(r"^(?P<acl_id>[0-9a-f-]+)/$", AclCreate.as_view(), name="aclcreate_urls"),
        url(r"^(?P<acl_id>[0-9a-f-]+)/new/$", AclCreate.as_view(), name="aclcreate_urls"),
    ])),

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

    re_path("approve/", include([
        url(r"^$", Acl_approve.as_view(), name="acl_approve_urls"),
        url(r"^(?P<acl_id>[0-9a-f-]+)/new/$", Acl_approve.as_view(), name="acl_approve_urls"),
        url(r"^(?P<acl_id>[0-9a-f-]+)/$", Acl_approve.as_view(), name="acl_approve_urls"),
    ])),

    re_path("pending/", include([
        url(r"^$", Acl_approve.as_view(), name="acl_pending_urls"),
        url(r"^(?P<acl_id>[0-9a-f-]+)/$", Acl_pending.as_view(), name="acl_pending_urls"), #(?P<token>[0-9a-z]{10})/
        #url(r"^(?P<acl_id>[0-9a-f-]+)/new/$", Acl_pending.as_view(), name="acl_pending_urls"),
    ])),

    path("checkip/<str:ip>/", CheckIp, name='check_ip_urls'),
    path("remove/", AclRemove, name="acl_remove"),
    path("change/", AclStageChange, name="acl_stage_change"),
    path("gitcheck/", Gitcheck, name="aclgit_urls"),
    path("overviewstatus/", OverViewStatus, name="aclcheck_status_urls"),
    url("$^", ACldefault, name="acldefault_urls")
]

