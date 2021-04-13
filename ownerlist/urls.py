from django.urls import path
from django.conf.urls import url
from .views import SearchView, TreeView, IpTable, Vpn, ip_save, ip_delete, ip_resolve, domain_resolve

urlpatterns = [
    #path('ipconfig/', SearchView.as_view(), name="ipconfig_urls"),
    url('iptable/ip-save/', ip_save, name="ipsave_urls"),
    url('iptable/ip-delete/', ip_delete, name="ipdelete_urls"),
    url('iptable/ipresolv/', ip_resolve, name="ipresolv_urls"),
    url('iptable/domainresolv/', domain_resolve, name="domainresolv_urls"),
    url('iptable/', IpTable.as_view(), name="iptable_urls"),
    url('search/', SearchView.as_view(), name="search"),
    url('vpn/', Vpn.as_view(), name="vpn"),
    url(r'^$', TreeView.as_view(), name="ipconfig_urls"),
]
