from django.shortcuts import render
from django.views.generic import View
from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse
from .forms import UploadFileForm
from .utils import upload_file_handler, ExtractDataXls, search_text


# Create your views here.
#vlan_fun = ExtractDataXls('D:\\Project\\acladmin-20210206T113742Z-001\\IP_LIST\\таблица ip адресов.xls') # ip\\172.18.0.Х Avaya.xls таблица ip адресов.xls ip\\195.239.64.хх.xls
#result = vlan_fun.execute_file_parsing() or 0


class TreeView(View):
    def get(self, request):
        return render(request, 'index.html')
    def post(self, request):
        return render(request, 'index.html')

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


