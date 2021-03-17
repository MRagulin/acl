from django.shortcuts import render
from django.views.generic import View
from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse
from .forms import UploadFileForm
from .utils import upload_file_handler, ExtractDataXls, search_text
from django.contrib import messages
import json
from django.shortcuts import redirect
from django.urls import reverse
import re


class IpTable(View):
    def get(self, request):
        return render(request, 'iptable.html')

    def post(self, request):
        result = None
        try:
            result = upload_file_handler(request)
        except Exception as e:
            if request.is_ajax:
                result = {'error': str(e)}
            else:
                messages.error(request, str(e))

        if request.method == 'POST' and request.is_ajax:
            return HttpResponse(json.dumps(result), content_type="application/text")
        return render(request, 'iptable.html', context=result)

class TreeView(View):
    def get(self, request):
        return render(request, 'index.html')


class SearchView(View):
    def get(self, request):
        context = {}
        search = request.path.split('/')
        result = search[2].strip().lower()
        if result == '':
                return redirect('ipconfig_urls')
        if search is not None:
            if re.match(r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}", result):
                return redirect(reverse('aclhistory_urls', kwargs={'acl_id': result}))
            context = search_text(request, result)
        return render(request, 'search.html', context=context)


class Vpn(View):
    def get(self, request):
        return render(request, 'vpn.html')
