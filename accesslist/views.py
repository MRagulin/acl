from django.shortcuts import render
from django.views.generic import View


class AclView(View):
    def get(self, requests):
        return render(requests, 'acl_base.html')
