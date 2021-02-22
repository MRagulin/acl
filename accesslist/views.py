from django.shortcuts import render
from django.views.generic import View
from ownerlist.utils import make_doc
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponse
import json

LOCAL_STORAGE:dict = {}
act:dict = {}
post_name_forms_key = [['name', 'email', 'tel', 'department', 'project', 'd_form', 'd_start', 'd_complete']]
FORM_APPLICATION_KEYS = ['contact', 'internal', 'dmz', 'external', 'traffic']
INFINITY = 'Нет'


def request_handler(requests, namespace=''):
    """Функция для заполнения глобального массива LOCAL_STORAGE из POST параметров файлов acl*"""
    global LOCAL_STORAGE
    KEY = 0
    if namespace == 'contact':
            LOCAL_STORAGE[namespace] = []
            for idx, post_key in enumerate(post_name_forms_key[0]):
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
                                KEY += 1
                            else:
                                LOCAL_STORAGE[namespace] = [[v]]
                        else:
                            if v != '':
                                LOCAL_STORAGE[namespace][KEY].append(v)
                            else:
                                return False



    #
    # elif namespace == 'internal':
    #     con_list:list = []
    #     for k, v in requests.POST.items():
    #         if 'input_' in str(k):
    #              if 'input__ip' in str(k):
    #                 if len(con_list) > 0:
    #                     if namespace in LOCAL_STORAGE:
    #                         LOCAL_STORAGE[namespace].append(con_list)
    #                         con_list.clear()
    #                     else:
    #                         LOCAL_STORAGE[namespace] = [con_list]
    #                         con_list.clear()
    #              if v != '':
    #                     con_list.append(v)
    #              else:
    #                  return False
    #     if len(con_list) > 0:
    #         if namespace in LOCAL_STORAGE:
    #             LOCAL_STORAGE[namespace].append(con_list)
    #             con_list.clear()
    #         else:
    #             LOCAL_STORAGE[namespace] = [con_list]
    return LOCAL_STORAGE

class AclTest(View):
    def get(self, request):
        return render(request, 'acl_test.html')

class AclOver(View):
    def get(self, request):
        global LOCAL_STORAGE
        file_download = None
        # data['contact'] = ['Рагулин Михаил Пиздабольевич', 'ragulinma@alfastrah.ru', '8(909)6971821', 'УИБ', 'Портал',
        #                    '18.02.2021', '28.02.2021', 'Нет']
        #
        # data['internal'] = [['172.16.1.1', '24', 'Внутренняя сеть AC'],
        #                     ['172.16.1.2', '24', 'Внутренняя сеть Кемерово']]
        #
        # data['dmz'] = [['195.239.64.79', '30', 'Z14-1709-gw.alfastrah.ru in Public'],
        #                ['195.239.64.79', '30', 'Z14-1709-gw.alfastrah.ru in Wild']]
        #
        # data['external'] = [['195.239.64.79', '30', 'Z14-1709-gw.alfastrah.ru in Public'],
        #                     ['195.239.64.79', '30', 'Z14-1709-gw.alfastrah.ru in Wild']]
        #
        # data['traffic'] = [['dpgw.alfastrah.ru', '195.239.64.162', 'Z14-1709-gw.alfastrah.ru', '195.239.64.79',
        #                     'TCP: 80,443,9000-9100', 'Функционал авто-ризации через ЕСИА 2.0'],
        #                    ['Z14-1709-gw.alfastrah.ru', '195.239.64.79',
        #                     'gosuslugi.ru www.gosuslugi.ru esia.gosuslugi.ru esia-por-tal1.test.gosuslugi.ru esia-por',
        #                     '-', 'TCP: 443', 'Доступ к ГИС']]

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