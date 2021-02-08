from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse, JsonResponse
from .forms import UploadFileForm
from .utils import upload_file_handler,ExcelHandler, ExtractDataXls


# Create your views here.


class SearchView(View):
    def get(self, request):
        vlan_fun = ExtractDataXls('D:\\Project\\acladmin-20210206T113742Z-001\\IP_LIST\\ip\\VLAN_CORE_ACI.xls')
        vlan_fun.execute_file_parsing()
        return render(request, 'index.html')

    def post(self, request):
        #response_data = upload_file_handler(request)
        #context = {'ip': response_data}
        #print(response_data)
        return render(request, 'index.html')
