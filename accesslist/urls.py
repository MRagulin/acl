from django.urls import path
from django.conf.urls import url
from .views import AclCreate, AclOver, AclCreate_StageOne, AclCreate_StageTwo, AclTest, AclCreate_StageThree, AclCreate_StageFour

urlpatterns = [
    path("overview/", AclOver.as_view(), name="acloverview_urls"),
    path("internal/", AclCreate_StageOne.as_view(), name="aclinternal_urls"),
    path("external/", AclCreate_StageThree.as_view(), name="aclexternal_urls"),
    path("traffic/", AclCreate_StageFour.as_view(), name="acltraffic_urls"),
    path("dmz/", AclCreate_StageTwo.as_view(), name="acldmz_urls"),
    path("create/", AclCreate.as_view(), name="aclcreate_urls"),
    path("test/", AclTest.as_view(), name="acltest_urls"),
]
