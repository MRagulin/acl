from django.shortcuts import render
from django.views.generic import View
from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse
from .forms import UploadFileForm
from .utils import upload_file_handler, ExtractDataXls, search_text
from django.contrib import messages
import json

# Create your views here.
#vlan_fun = ExtractDataXls('D:\\Project\\acladmin-20210206T113742Z-001\\IP_LIST\\таблица ip адресов.xls') # ip\\172.18.0.Х Avaya.xls таблица ip адресов.xls ip\\195.239.64.хх.xls
#result = vlan_fun.execute_file_parsing() or 0

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
    # def post(self, request):
    #     result = ExtractDataXls(request, "/tmp/ip.xls")
    #     return render(request, 'index.html', context=result)

class SearchView(View):
    def get(self, request):
        context = {}
        search = request.path.split('/')
        result = search[2].strip().lower()
        if result == '':
                return redirect('ipconfig_urls')
        if search is not None:
            context = search_text(request, result)
        return render(request, 'search.html', context=context)


