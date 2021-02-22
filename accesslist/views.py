from django.shortcuts import render
from django.views.generic import View
from ownerlist.utils import make_doc
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponse
import json

LOCAL_STORAGE:dict = {}  # Хранение данных для заполнения docx
LOCAL_ACTION:dict = {}  # Хранение данных для активностей: docx, git, omni

FORM_APPLICATION_KEYS = ['contact', 'internal', 'dmz', 'external', 'traffic']
POST_FORM_KEYS = ['name', 'email', 'tel', 'department', 'project', 'd_form', 'd_start', 'd_complete']


def request_handler(requests, namespace=''):
    """Функция для заполнения глобального массива LOCAL_STORAGE из POST параметров файлов acl*"""
    INFINITY = 'Нет'
    global LOCAL_STORAGE
    cnt_key = 0
    if namespace == 'contact':
            LOCAL_STORAGE[namespace] = []
            for idx, post_key in enumerate(POST_FORM_KEYS):
                if idx == 7:
                    if requests.POST.get(post_key) == 'on':
                        LOCAL_STORAGE[namespace].append(INFINITY)
                else:
                    if requests.POST.get(post_key) != '':
                        LOCAL_STORAGE[namespace].append(requests.POST.get(post_key))
                    else:
                        return False

    else:
        if namespace == 'traffic':
            str_pattern = 'input__domain_source'
        else:
            str_pattern = 'input__ip'

        for k, v in requests.POST.items():
                if 'input_' in str(k):
                        if str_pattern in str(k):
                            if namespace in LOCAL_STORAGE:
                                LOCAL_STORAGE[namespace].append([v])
                                cnt_key += 1
                            else:
                                LOCAL_STORAGE[namespace] = [[v]]
                        else:
                            if v != '':
                                LOCAL_STORAGE[namespace][cnt_key].append(v)
                            else:
                                return False
    return LOCAL_STORAGE


class AclTest(View):
    def get(self, request):
        return render(request, 'acl_test.html')


class AclOver(View):
    def get(self, request):
        global LOCAL_STORAGE
        file_download = None
        if len(LOCAL_STORAGE) >= 4 and all(KEY in LOCAL_STORAGE for KEY in FORM_APPLICATION_KEYS):
            file_download = make_doc(LOCAL_STORAGE)
            LOCAL_STORAGE = {}
        return render(request, 'acl_overview.html', context={'file_download': file_download})


class AclCreate(View):
    def get(self, request):
        return render(request, 'acl_create_info.html')
    def post(self, request):
        if request.method == 'POST' and request.is_ajax and request_handler(request, 'contact'):
            return HttpResponseRedirect(reverse('aclinternal_urls'))
        else:
            messages.warning(request, 'Не все поля заполнены')
            return render(request, 'acl_create_info.html')

# class AclInfo(View):
#     def get(self, request):
#         return render(request, 'acl_create_info.html')


class AclCreate_internal(View):
    def get(self, request):
        return render(request, 'acl_internal_resources.html')

    def post(self, request):
        if request.method == 'POST' and request.is_ajax and request_handler(request, 'internal'):
            return HttpResponseRedirect(reverse('acldmz_urls'))  #acl_dmz_resources
        else:
            messages.warning(request, 'Не все поля заполнены')
            return render(request, 'acl_internal_resources.html')



class AclCreate_dmz(View):
    def get(self, request):
        return render(request, 'acl_dmz_resources.html')

    def post(self, request):
        if request.method == 'POST' and request.is_ajax and request_handler(request, 'dmz'):
            return HttpResponseRedirect(reverse('aclexternal_urls'))  #acl_dmz_resources
        else:
            messages.warning(request, 'Не все поля заполнены')
            return render(request, 'acl_dmz_resources.html')


class AclCreate_external(View):
    def get(self, request):
        return render(request, 'acl_external_resources.html')

    def post(self, request):
        if request.method == 'POST' and request.is_ajax and request_handler(request, 'external'):
            return HttpResponseRedirect(reverse('acltraffic_urls'))  #acl_dmz_resources
        else:
            messages.warning(request, 'Не все поля заполнены')
            return render(request, 'acl_external_resources.html')


class AclCreate_traffic(View):
    def get(self, request):
        return render(request, 'acl_traffic.html')

    def post(self, request):
        if request.method == 'POST' and request.is_ajax and request_handler(request, 'traffic'):
            return HttpResponseRedirect(reverse('acloverview_urls'))  #acl_dmz_resources
        else:
            messages.warning(request, 'Не все поля заполнены')
            return render(request, 'acl_traffic.html')