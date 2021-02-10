from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse, JsonResponse
from .forms import UploadFileForm
from .utils import upload_file_handler, ExtractDataXls


# Create your views here.


class SearchView(View):
    def get(self, request):
        vlan_fun = ExtractDataXls('D:\\Project\\acladmin-20210206T113742Z-001\\IP_LIST\\таблица ip адресов.xls') # ip\\172.18.0.Х Avaya.xls таблица ip адресов.xls ip\\195.239.64.хх.xls
        result = vlan_fun.execute_file_parsing() or 0
        return render(request, 'index.html', context={'count': result})

    def post(self, request):
        #response_data = upload_file_handler(request)
        #context = {'ip': response_data}
        #print(response_data)
        return render(request, 'index.html')
