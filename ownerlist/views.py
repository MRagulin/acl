from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse, JsonResponse
from .forms import UploadFileForm
from .utils import upload_file_handler,ExcelHandler


# Create your views here.


class SearchView(View):
    def get(self, request):
        return render(request, 'index.html')

    def post(self, request):
        response_data = upload_file_handler(request, ExcelHandler)
        context = {'ip': response_data}
        #print(response_data)
        return render(request, 'index.html', context)
